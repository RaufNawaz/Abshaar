#!/usr/bin/env bash
# Bootstrap, train, fuse, export, evaluate and pack -- one command.
#
# Each stage records a marker under <root>/.stages and is skipped when it is
# already done, so re-running after an interruption resumes rather than
# restarting.
#
# Usage: ./run_all.sh [-r work_root] [-m model_repo] [-i iters]
#                     [--skip-gguf] [--skip-generate] [--resume]

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

ROOT_ARG=""
MODEL="mlx-community/Qwen3-8B-4bit"
ITERS=600
SKIP_GGUF=""
SKIP_GENERATE=0
RESUME=""
while [ $# -gt 0 ]; do
    case "$1" in
        -r|--root)  ROOT_ARG="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        -i|--iters) ITERS="$2"; shift 2 ;;
        --skip-gguf) SKIP_GGUF="--skip-gguf"; shift ;;
        --skip-generate) SKIP_GENERATE=1; shift ;;
        --resume) RESUME="--resume"; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

init_env "$(resolve_root "$ROOT_ARG")"
START=$(date +%s)
SLUG="$(run_slug "$MODEL")"

head_ "Abshaar - Bulleh Shah expert model, full run"
note_ "root:  $ROOT"
note_ "model: $MODEL"
note_ "Rough timings on a Mac Studio: bootstrap 10-30 min (download-bound),"
note_ "training 20-90 min at $ITERS iters, fuse a few minutes, generations 15-40 min."

"$BUNDLE_DIR/00_bootstrap.sh" -r "$ROOT" -m "$MODEL"

if stage_done "train_$SLUG" && [ -z "$RESUME" ]; then
    note_ "Training already completed for $MODEL; skipping (rm $ROOT/.stages/train_$SLUG to redo)."
else
    "$BUNDLE_DIR/01_train.sh" -r "$ROOT" -m "$MODEL" -i "$ITERS" $RESUME
fi

"$BUNDLE_DIR/02_fuse_export.sh" -r "$ROOT" -m "$MODEL" $SKIP_GGUF

if [ "$SKIP_GENERATE" = "0" ]; then
    "$BUNDLE_DIR/03_generate.sh" -r "$ROOT" -m "$MODEL"
fi

"$BUNDLE_DIR/04_pack_outbox.sh" -r "$ROOT" -m "$MODEL"

head_ "Full run finished in $(( ($(date +%s) - START) / 60 )) minutes"
