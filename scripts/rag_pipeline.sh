#!/usr/bin/env bash
# Resumable path from "trained adapter on disk" to "a model that answers
# questions". Every stage is idempotent and writes a marker; re-running the
# script skips finished stages. Safe to kill and restart at any point.
#
#   ./scripts/rag_pipeline.sh            # run all remaining stages
#   ./scripts/rag_pipeline.sh status     # show what is done, run nothing
#   ./scripts/rag_pipeline.sh 1 2 3      # run only these stages
#   ./scripts/rag_pipeline.sh --redo 1   # clear stage 1's marker, then run it
#
# Requires training/RUN_AUTHORIZED (Rauf's deliberate switch: see
# training/README.md). Stages 3+ invoke models and will warm the machine.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
STATE="$ROOT/training/.pipeline_state"
LOGS="$ROOT/training/pipeline_logs"
OUT="$ROOT/training/rag_outputs"
mkdir -p "$STATE" "$LOGS" "$OUT"
ABSHAAR="$ROOT/scripts/abshaar.sh"
STAMP="$(date +%Y%m%d-%H%M%S)"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
done_marker() { echo "$STATE/stage${1}.done"; }
is_done() { [ -f "$(done_marker "$1")" ]; }
mark()    { date -u +"%Y-%m-%dT%H:%M:%SZ" > "$(done_marker "$1")"; }

STAGE_NAMES=(
  [1]="build-index            embed the 1,306-record KB into Chroma"
  [2]="retrieve-smoke         retrieval only, no model invoked"
  [3]="ask-demo               grounded answers via base qwen3:8b + RAG"
  [4]="baseline-base          run-eval, bare model, 50 standard probes"
  [5]="baseline-base-rag      run-eval --rag, fills EVAL_MATRIX base+RAG"
  [6]="fetch-mlx-base         download mlx-community/Qwen3-8B-4bit (~4.5 GB)"
  [7]="tuned-generate         run 2 adapter answers the same demo questions"
)

require_auth() {
  [ -f "$ROOT/training/RUN_AUTHORIZED" ] || {
    echo "REFUSING: training/RUN_AUTHORIZED does not exist." >&2
    echo "This switch is deliberate. Create it only when Rauf has said so." >&2
    exit 2
  }
}

ollama_up() { curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; }
ensure_ollama() {
  ollama_up && return 0
  say "starting ollama serve"
  nohup ollama serve > "$LOGS/ollama-$STAMP.log" 2>&1 &
  for _ in $(seq 1 30); do sleep 1; ollama_up && return 0; done
  echo "ollama did not come up; see $LOGS/ollama-$STAMP.log" >&2; return 1
}

stage1() {  # build-index -- must be all-or-nothing
  local manifest="$ROOT/data/cache/chroma/manifest.json"
  if [ -f "$manifest" ]; then
    say "stage 1: index already built ($(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["records"])' "$manifest") records)"
  else
    # Resume rather than restart. `abshaar build-index` rebuilds from zero and
    # rag.py's _collection(create=True) deletes the collection first, so an
    # interrupted run costs the whole ~45 min of BGE-M3 encoding. The resumable
    # builder asks the collection which ids it already holds and does only the
    # rest, so a kill costs one batch.
    say "stage 1: build-index, resuming if a previous run was interrupted"
    "$ROOT/.venv/bin/python" "$ROOT/scripts/build_index_resumable.py" 2>&1 \
      | tee "$LOGS/build-index-$STAMP.log"
    [ -f "$manifest" ] || { echo "build-index finished without a manifest" >&2; return 1; }
  fi
  mark 1
}

stage2() {  # retrieval only -- proves the index without invoking any model
  say "stage 2: retrieval smoke test (no generation)"
  local f="$OUT/retrieval_smoke.txt"
  : > "$f"
  while IFS= read -r q; do
    [ -z "$q" ] && continue
    { echo "### $q"; "$ABSHAAR" ask --retrieve-only --k 5 "$q"; echo; } >> "$f"
  done < "$ROOT/training/demo_questions.txt"
  tail -40 "$f"
  echo "-> $f"
  mark 2
}

stage3() {
  require_auth; ensure_ollama
  say "stage 3: grounded answers (base qwen3:8b + RAG)"
  local f="$OUT/answers_base_rag.md"
  : > "$f"
  while IFS= read -r q; do
    [ -z "$q" ] && continue
    { echo "## $q"; echo; "$ABSHAAR" ask "$q"; echo; } >> "$f"
    echo "  answered: $q"
  done < "$ROOT/training/demo_questions.txt"
  echo "-> $f"
  mark 3
}

stage4() {
  require_auth; ensure_ollama
  say "stage 4: baseline, bare qwen3:8b over the 50 standard probes"
  "$ABSHAAR" run-eval --model qwen3:8b 2>&1 | tee "$LOGS/eval-base-$STAMP.log"
  mark 4
}

stage5() {
  require_auth; ensure_ollama
  say "stage 5: baseline, qwen3:8b + RAG"
  "$ABSHAAR" run-eval --model qwen3:8b --rag 2>&1 | tee "$LOGS/eval-base-rag-$STAMP.log"
  mark 5
}

stage6() {
  require_auth
  say "stage 6: fetching mlx-community/Qwen3-8B-4bit (~4.5 GB, one time)"
  "$ROOT/.venv/bin/python" - <<'PY' 2>&1 | tee "$LOGS/fetch-base-$STAMP.log"
from huggingface_hub import snapshot_download
p = snapshot_download("mlx-community/Qwen3-8B-4bit")
print("cached at", p)
PY
  mark 6
}

stage7() {
  require_auth
  local adapter="$ROOT/training/adapters/mlx-community_Qwen3-8B-4bit-run2"
  [ -f "$adapter/adapters.safetensors" ] || { echo "run 2 adapter missing at $adapter" >&2; return 1; }
  say "stage 7: run 2 adapter answering the demo questions (no RAG -- this is the LoRA alone)"
  local f="$OUT/answers_tuned_norag.md"
  : > "$f"
  while IFS= read -r q; do
    [ -z "$q" ] && continue
    { echo "## $q"; echo; } >> "$f"
    "$ROOT/.venv/bin/python" -m mlx_lm generate \
      --model mlx-community/Qwen3-8B-4bit \
      --adapter-path "$adapter" \
      --max-tokens 400 \
      --prompt "$q" 2>/dev/null >> "$f" || echo "(generation failed)" >> "$f"
    echo >> "$f"
    echo "  answered: $q"
  done < "$ROOT/training/demo_questions.txt"
  echo "-> $f"
  mark 7
}

show_status() {
  echo "Pipeline state ($STATE):"
  for i in 1 2 3 4 5 6 7; do
    if is_done "$i"; then printf "  [x] %d  %s   (%s)\n" "$i" "${STAGE_NAMES[$i]}" "$(cat "$(done_marker "$i")")"
    else printf "  [ ] %d  %s\n" "$i" "${STAGE_NAMES[$i]}"; fi
  done
}

# ---- dispatch ----
if [ "${1:-}" = "status" ]; then show_status; exit 0; fi
if [ "${1:-}" = "--redo" ]; then shift; for s in "$@"; do rm -f "$(done_marker "$s")"; done; fi

WANTED=("$@")
[ ${#WANTED[@]} -eq 0 ] && WANTED=(1 2 3 4 5 6 7)

for s in "${WANTED[@]}"; do
  if is_done "$s"; then echo "== stage $s already done, skipping (--redo $s to force)"; continue; fi
  "stage$s"
done

echo; show_status
