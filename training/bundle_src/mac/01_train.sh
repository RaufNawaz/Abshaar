#!/usr/bin/env bash
# LoRA fine-tune with mlx-lm on Apple Silicon.
#
# mlx-lm checkpoints every --save-every iterations into the adapter folder,
# so an interrupted run can be continued with --resume.
#
# Usage: ./01_train.sh [-r work_root] [-m model_repo] [-i iters] [--lr rate]
#                      [-t tag] [--init-from ADAPTER] [--resume]
#
# --resume    continue THIS run in place (same folder, same adapter file)
# --init-from warm-start a NEW run from another run's adapter. Pair it with
#             -t so the new run gets its own folder: mlx-lm restarts the
#             iteration counter at 1, so without a tag its checkpoints would
#             overwrite the ones you are warm-starting from.

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

ROOT_ARG=""
MODEL="mlx-community/Qwen3-8B-4bit"
ITERS=600
BATCH=2
# mlx-lm's own default is 1e-5 (mlx_lm/lora.py), which is conservative for
# LoRA. Raised to 1e-4 on 2026-08-31 at Rauf's instruction, sitting between
# mlx-lm's default and the CUDA bundle's 2e-4.
#
# Note what this does and does not do: a higher learning rate takes LARGER
# STEPS, not faster ones. Wall clock is iterations x seconds-per-iteration,
# so 1e-4 at the same --iters costs exactly as long as 1e-5 did. The saving
# comes from needing FEWER iterations to reach the same loss -- so pair this
# with a lower -i (try 800-1000 against the 1560 that ~3 epochs needs at
# 1e-5) and confirm against the validation curve rather than assuming.
LR=1e-4
RESUME=0
TAG=""
INIT_FROM=""
while [ $# -gt 0 ]; do
    case "$1" in
        -r|--root)  ROOT_ARG="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        -i|--iters) ITERS="$2"; shift 2 ;;
        -b|--batch-size) BATCH="$2"; shift 2 ;;
        --lr|--learning-rate) LR="$2"; shift 2 ;;
        -t|--tag)   TAG="$2"; shift 2 ;;
        --init-from) INIT_FROM="$2"; shift 2 ;;
        --resume)   RESUME=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

init_env "$(resolve_root "$ROOT_ARG")"
require_venv

SLUG="$(run_slug "$MODEL")"
[ -n "$TAG" ] && SLUG="$SLUG-$TAG"
RUN_DIR="$ROOT/runs/$SLUG"
ADAPTER_DIR="$RUN_DIR/adapter"
mkdir -p "$ADAPTER_DIR"

head_ "Training LoRA on $MODEL"
note_ "data:    $BUNDLE_DIR/dataset"
note_ "adapter: $ADAPTER_DIR"
note_ "iters:   $ITERS (batch $BATCH, learning rate $LR)"
[ -n "$TAG" ] && note_ "tag:     $TAG"

# An array, not a string: the bundle or the work root may sit under a path
# containing spaces, and an unquoted $ARGS would split "--data /My Folder/x"
# into two arguments and hand mlx-lm a truncated path.
ARGS=(--model "$MODEL" --train
      --data "$BUNDLE_DIR/dataset"
      --batch-size "$BATCH"
      --iters "$ITERS"
      --adapter-path "$ADAPTER_DIR"
      --learning-rate "$LR"
      --save-every 200 --steps-per-report 25 --steps-per-eval 100)
if [ -n "$INIT_FROM" ]; then
    if [ -d "$INIT_FROM" ]; then
        INIT_FROM="$INIT_FROM/adapters.safetensors"
    fi
    if [ ! -f "$INIT_FROM" ]; then
        echo "ERROR: --init-from '$INIT_FROM' is not an adapter file." >&2
        exit 1
    fi
    if [ "$INIT_FROM" = "$ADAPTER_DIR/adapters.safetensors" ]; then
        echo "ERROR: --init-from points at this run's own output directory." >&2
        echo "       Pass -t <tag> so the new run writes somewhere else, or use --resume." >&2
        exit 1
    fi
    note_ "Warm start: $INIT_FROM"
    note_ "mlx-lm restores adapter WEIGHTS only -- optimizer state restarts and"
    note_ "the iteration counter restarts at 1. This is a new run, warm-started."
    ARGS+=(--resume-adapter-file "$INIT_FROM")
elif [ "$RESUME" = "1" ] && [ -f "$ADAPTER_DIR/adapters.safetensors" ]; then
    note_ "Resuming in place from $ADAPTER_DIR/adapters.safetensors"
    ARGS+=(--resume-adapter-file "$ADAPTER_DIR/adapters.safetensors")
fi

START=$(date +%s)
LOG="$ROOT/logs/train-$(date +%Y%m%d-%H%M%S).log"
# tee would otherwise mask a training failure behind its own exit code.
set +e
mlx_run lora "${ARGS[@]}" 2>&1 | tee "$LOG"
TRAIN_STATUS=${PIPESTATUS[0]}
set -e
if [ "$TRAIN_STATUS" -ne 0 ]; then
    echo "ERROR: training failed (exit $TRAIN_STATUS); full output in $LOG" >&2
    exit 1
fi
ELAPSED=$(( $(date +%s) - START ))

"$PY" - "$MODEL" "$RUN_DIR" "$ADAPTER_DIR" "$BUNDLE_DIR/dataset" "$ITERS" "$BATCH" "$ELAPSED" "$LR" <<'PYSUM'
import hashlib, json, platform, sys, time
from pathlib import Path

model, run_dir, adapter_dir, data_dir, iters, batch, elapsed, lr = sys.argv[1:9]
run_dir, adapter_dir, data_dir = Path(run_dir), Path(adapter_dir), Path(data_dir)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def count(path):
    with path.open(encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())

weights = adapter_dir / "adapters.safetensors"
try:
    import mlx.core as mx
    mlx_version = mx.__version__
except Exception:
    mlx_version = "unknown"

summary = {
    "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "base_model": model,
    "toolchain": "mlx-lm",
    "adapter_dir": str(adapter_dir),
    "adapter_sha256": sha256(weights) if weights.exists() else None,
    "dataset": {
        "train_examples": count(data_dir / "train.jsonl"),
        "train_sha256": sha256(data_dir / "train.jsonl"),
        "valid_examples": count(data_dir / "valid.jsonl"),
        "valid_sha256": sha256(data_dir / "valid.jsonl"),
    },
    "hyperparameters": {"iters": int(iters), "batch_size": int(batch),
                        "learning_rate": float(lr), "optimizer": "adam (mlx-lm default)",
                        "save_every": 200, "steps_per_eval": 100},
    "results": {"train_runtime_seconds": int(elapsed)},
    "environment": {"python": sys.version.split()[0], "platform": platform.platform(), "mlx": mlx_version},
    "note": "Val loss is in the training log; mlx-lm prints it every --steps-per-eval.",
}
(run_dir / "train_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("adapter sha256:", summary["adapter_sha256"])
print("summary:", run_dir / "train_summary.json")
PYSUM

stage_mark "train_$SLUG"
head_ "Training done in $((ELAPSED / 60)) min"
note_ "Next: ./02_fuse_export.sh -r \"$ROOT\" -m $MODEL"
