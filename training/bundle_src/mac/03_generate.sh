#!/usr/bin/env bash
# Base vs tuned answers on the held-out eval set and the honesty probes.
# Evidence, not the acceptance evaluation -- see generate_outputs_mlx.py.
#
# Usage: ./03_generate.sh [-r work_root] [-m model_repo] [--skip-base]

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

ROOT_ARG=""
MODEL="mlx-community/Qwen3-8B-4bit"
TAG=""
SKIP_BASE=0
MAX_TOKENS=512
LIMIT=0
while [ $# -gt 0 ]; do
    case "$1" in
        -r|--root)  ROOT_ARG="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        -t|--tag)   TAG="$2"; shift 2 ;;
        --max-tokens) MAX_TOKENS="$2"; shift 2 ;;
        --limit)    LIMIT="$2"; shift 2 ;;
        --skip-base) SKIP_BASE=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done
# MLX generates one prompt at a time, so 193 items x 2 models is usually the
# longest stage of the run. --limit N time-boxes it to the first N of each set.
LIMIT_ARGS=()
[ "$LIMIT" != "0" ] && LIMIT_ARGS=(--limit "$LIMIT")

init_env "$(resolve_root "$ROOT_ARG")"
require_venv

SLUG="$(run_slug "$MODEL")"
[ -n "$TAG" ] && SLUG="$SLUG-$TAG"
ADAPTER_DIR="$ROOT/runs/$SLUG/adapter"
OUT_DIR="$ROOT/outbox/generations"
[ -d "$ADAPTER_DIR" ] || { echo "ERROR: no adapter at $ADAPTER_DIR -- run ./01_train.sh first." >&2; exit 1; }

if [ "$SKIP_BASE" = "0" ]; then
    head_ "Generating BASE answers (untuned $MODEL)"
    "$PY" "$BUNDLE_DIR/generate_outputs_mlx.py" --model "$MODEL" \
        --data-dir "$BUNDLE_DIR/dataset" --out-dir "$OUT_DIR" --tag base --max-tokens "$MAX_TOKENS" ${LIMIT_ARGS+"${LIMIT_ARGS[@]}"}
fi

head_ "Generating TUNED answers (adapter applied)"
"$PY" "$BUNDLE_DIR/generate_outputs_mlx.py" --model "$MODEL" --adapter "$ADAPTER_DIR" \
    --data-dir "$BUNDLE_DIR/dataset" --out-dir "$OUT_DIR" --tag tuned --max-tokens "$MAX_TOKENS" ${LIMIT_ARGS+"${LIMIT_ARGS[@]}"}

head_ "Generations written"
ls -lh "$OUT_DIR"
note_ "These are unscored. Scoring happens with the project's rubric on the serving Mac."
note_ "Next: ./04_pack_outbox.sh -r \"$ROOT\" -m $MODEL"
