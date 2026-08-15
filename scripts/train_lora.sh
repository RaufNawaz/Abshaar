#!/usr/bin/env bash
# Phase 5 Path A: local LoRA fine-tune on Apple Silicon via mlx-lm.
# macOS-only by nature (MLX); no .ps1 twin — cloud Path B covers non-Mac.
#
# Usage (from repo root):
#   ./scripts/train_lora.sh [model_repo] [iters]
# Defaults: mlx-community/Qwen3-4B-4bit, 600 iters.
#
# Prereqs: .venv with mlx-lm installed; data exported via
#   ./scripts/abshaar.sh export-mlx-dataset
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$REPO_ROOT/.venv/bin/python"
MODEL="${1:-mlx-community/Qwen3-4B-4bit}"
ITERS="${2:-600}"
DATA_DIR="$REPO_ROOT/data/processed/training/mlx"
ADAPTER_DIR="$REPO_ROOT/training/adapters/$(echo "$MODEL" | tr '/:' '__')"

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: .venv python not found; create the venv and install requirements first." >&2
    exit 1
fi
if [ ! -f "$DATA_DIR/train.jsonl" ]; then
    echo "ERROR: $DATA_DIR/train.jsonl missing; run ./scripts/abshaar.sh export-mlx-dataset first." >&2
    exit 1
fi

"$PYTHON" -c "import mlx_lm" 2>/dev/null || "$PYTHON" -m pip install --quiet mlx-lm

mkdir -p "$ADAPTER_DIR"
echo "Training LoRA: model=$MODEL iters=$ITERS adapters=$ADAPTER_DIR"
"$PYTHON" -m mlx_lm lora \
    --model "$MODEL" \
    --train \
    --data "$DATA_DIR" \
    --batch-size 2 \
    --iters "$ITERS" \
    --adapter-path "$ADAPTER_DIR" \
    --save-every 200 \
    --steps-per-report 25 \
    --steps-per-eval 100

echo "Done. Adapters in $ADAPTER_DIR"
echo "Next: evaluate with the plan's Phase 5 gate before accepting."
