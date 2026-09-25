#!/usr/bin/env bash
# Unattended run to fill every row of training/EVAL_MATRIX.md.
#
# Sequence matters and is not arbitrary:
#   4  base qwen3:8b, bare        (Ollama)
#   5  base qwen3:8b + RAG        (Ollama + Chroma)
#   -- stop Ollama's 8B, start the mlx server --
#   8  run 2 adapter, bare        (mlx)
#   9  run 2 adapter + RAG        (mlx + Chroma, judge still Ollama qwen3:4b)
#
# 8 and 9 come last because Ollama holding qwen3:8b and an mlx server holding
# the 4-bit 8B is ~11 GB on a 16 GB Air. Stages 8/9 keep Ollama available for
# the JUDGE only (qwen3:4b, ~3 GB), which the two-phase eval loads after all
# answering is done, so the two big models never need to be resident together.
#
# Every step is skipped if its marker exists, and run-eval checkpoints per
# probe, so this can be killed and restarted at any point.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
STATE="$ROOT/training/.pipeline_state"
LOGS="$ROOT/training/pipeline_logs"
mkdir -p "$STATE" "$LOGS"
STAMP="$(date +%Y%m%d-%H%M%S)"
JOURNAL="$LOGS/overnight-$STAMP.md"

log() { printf '%s  %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$JOURNAL"; }
is_done() { [ -f "$STATE/stage$1.done" ]; }
mark() { date -u +"%Y-%m-%dT%H:%M:%SZ" > "$STATE/stage$1.done"; }

ollama_up() { curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; }
mlx_up()    { curl -fsS http://127.0.0.1:8080/health >/dev/null 2>&1 || curl -fsS http://127.0.0.1:8080/v1/models >/dev/null 2>&1; }

ensure_ollama() {
  ollama_up && return 0
  nohup ollama serve > "$LOGS/ollama-$STAMP.log" 2>&1 &
  for _ in $(seq 1 30); do sleep 1; ollama_up && return 0; done
  return 1
}

log "overnight run starting"

# --- wait for anything already in flight ------------------------------------
if pgrep -f "rag_pipeline.sh 4" >/dev/null 2>&1; then
  log "stage 4 already running; waiting for it"
  while pgrep -f "rag_pipeline.sh 4" >/dev/null 2>&1; do sleep 30; done
  log "stage 4 process exited"
fi

# --- stages 4 and 5: the Ollama baselines -----------------------------------
for stage in 4 5; do
  if is_done "$stage"; then log "stage $stage already done"; continue; fi
  ensure_ollama || { log "FATAL: no ollama"; exit 1; }
  log "stage $stage starting"
  if "$ROOT/scripts/rag_pipeline.sh" "$stage" >> "$LOGS/overnight-stage$stage.log" 2>&1; then
    log "stage $stage OK"
  else
    log "stage $stage FAILED (exit $?) -- see overnight-stage$stage.log; continuing"
  fi
done

# --- free the 8B before loading another one ---------------------------------
log "unloading qwen3:8b from Ollama (keeps the judge model available)"
curl -fsS http://127.0.0.1:11434/api/generate \
  -d '{"model":"qwen3:8b","keep_alive":0}' >/dev/null 2>&1 || true
sleep 5

# --- start the mlx server with run 2's adapter ------------------------------
if ! mlx_up; then
  log "starting mlx_lm.server with run 2's adapter"
  nohup "$ROOT/scripts/serve_tuned.sh" run2 > "$LOGS/mlx-server-$STAMP.log" 2>&1 &
  for _ in $(seq 1 120); do sleep 5; mlx_up && break; done
fi
if mlx_up; then
  log "mlx server up on :8080"
else
  log "FATAL: mlx server never came up -- see mlx-server-$STAMP.log"
  exit 1
fi

# --- stages 8 and 9: the tuned rows -----------------------------------------
run_tuned_eval() {  # $1 = stage, $2 = extra flags, $3 = label
  local stage="$1" flags="$2" label="$3"
  if is_done "$stage"; then log "stage $stage ($label) already done"; return 0; fi
  ensure_ollama || log "warning: no ollama, the judge will degrade to token-F1"
  log "stage $stage starting: $label"
  # shellcheck disable=SC2086
  if "$ROOT/scripts/abshaar.sh" run-eval --model mlx:run2 $flags \
       >> "$LOGS/overnight-stage$stage.log" 2>&1; then
    mark "$stage"; log "stage $stage OK"
  else
    log "stage $stage FAILED (exit $?) -- resumable, see overnight-stage$stage.log"
  fi
}

run_tuned_eval 8 ""      "run 2 adapter, bare"
run_tuned_eval 9 "--rag" "run 2 adapter + RAG"

log "stopping mlx server"
pkill -f "mlx_lm server" 2>/dev/null || true

log "overnight run finished"
echo >> "$JOURNAL"
echo '## eval_baseline.md' >> "$JOURNAL"
cat "$ROOT/data/processed/training/eval_baseline.md" >> "$JOURNAL" 2>/dev/null || \
  echo '(not written)' >> "$JOURNAL"
log "journal: $JOURNAL"
