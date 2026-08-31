#!/usr/bin/env bash
# Imports a LoRA adapter directory trained elsewhere (a Mac Studio or the
# Windows/CUDA workstation -- see docs/18) into this repo's training/adapters/,
# so docs/17 Training Runbook §6 (fuse/serve/eval) can continue on this
# machine. Accepts both toolchains' output: mlx-lm writes
# adapters.safetensors, peft writes adapter_model.safetensors.
#
# Usage (from repo root):
#   ./scripts/import_trained_adapter.sh /path/to/returned/adapters/<model-name>
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SRC="${1:?usage: $0 /path/to/returned/adapters/<model-name>}"
if [[ ! -d "$SRC" ]]; then
  echo "ERROR: $SRC is not a directory." >&2
  exit 1
fi
if [[ ! -f "$SRC/adapters.safetensors" && ! -f "$SRC/adapter_model.safetensors" && -z "$(find "$SRC" -maxdepth 1 -name '*.safetensors' -print -quit)" ]]; then
  echo "ERROR: no .safetensors file found directly inside $SRC -- this doesn't look like an mlx_lm or peft adapter output." >&2
  exit 1
fi

NAME="$(basename "$SRC")"
DEST="$REPO_ROOT/training/adapters/$NAME"
if [[ -e "$DEST" ]]; then
  echo "ERROR: $DEST already exists. Move it aside first if you want to replace it." >&2
  exit 1
fi

mkdir -p "$REPO_ROOT/training/adapters"
cp -R "$SRC" "$DEST"

echo "Imported into: $DEST"
echo
echo "SHA-256 of adapter weight file(s):"
find "$DEST" -maxdepth 1 -name '*.safetensors' -print0 | xargs -0 shasum -a 256

echo
echo "Record that SHA-256 plus training args (model, iters, val loss) in"
echo "OFFLOADING.md and training/EVAL_MATRIX.md, then continue with"
echo "docs/17_training_runbook.md §6 (fuse -> import to Ollama -> acceptance eval)."
