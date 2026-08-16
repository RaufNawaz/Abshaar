#!/usr/bin/env bash
# Packages ONLY the gated, leak-scanned mlx training dataset plus a
# standalone training script into training/portable_bundle/ — small enough
# to carry on any drive/AirDrop to a Mac Studio (or any other Apple Silicon
# machine) for the actual LoRA training run, without bringing the private
# knowledge base, Sufinama witness texts, Rafat's copyrighted reference
# translations, or repo git history onto a shared/lab machine.
#
# Usage (from repo root, on this Mac):
#   ./scripts/export_training_bundle.sh [model_repo] [iters]
# Defaults match train_lora.sh's own defaults (mlx-community/Qwen3-4B-4bit,
# 600 iters) -- pass a bigger model (e.g. mlx-community/Qwen3-8B-4bit) if the
# target machine has the RAM for it; see the printed MANIFEST for guidance.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

MODEL="${1:-mlx-community/Qwen3-4B-4bit}"
ITERS="${2:-600}"
DATA_SRC="data/processed/training/mlx"
BUNDLE="training/portable_bundle"

if [[ ! -f "$DATA_SRC/train.jsonl" || ! -f "$DATA_SRC/valid.jsonl" ]]; then
  echo "ERROR: $DATA_SRC/{train,valid}.jsonl missing; run ./scripts/abshaar.sh export-mlx-dataset first." >&2
  exit 1
fi

rm -rf "$BUNDLE"
mkdir -p "$BUNDLE/dataset"
cp "$DATA_SRC/train.jsonl" "$BUNDLE/dataset/train.jsonl"
cp "$DATA_SRC/valid.jsonl" "$BUNDLE/dataset/valid.jsonl"

TRAIN_COUNT=$(wc -l <"$BUNDLE/dataset/train.jsonl" | tr -d ' ')
VALID_COUNT=$(wc -l <"$BUNDLE/dataset/valid.jsonl" | tr -d ' ')
TRAIN_SHA=$(shasum -a 256 "$BUNDLE/dataset/train.jsonl" | awk '{print $1}')
VALID_SHA=$(shasum -a 256 "$BUNDLE/dataset/valid.jsonl" | awk '{print $1}')

cat >"$BUNDLE/train_standalone.sh" <<'SCRIPT'
#!/usr/bin/env bash
# Standalone LoRA trainer for a Mac Studio / any Apple Silicon Mac. Needs only
# this folder (no repo checkout) plus Python 3.10+ and internet access to
# pull the base model + mlx-lm from PyPI/Hugging Face on first run.
#
# Usage (from inside this bundle folder):
#   ./train_standalone.sh [model_repo] [iters]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL="${1:-__MODEL__}"
ITERS="${2:-__ITERS__}"
DATA_DIR="$HERE/dataset"
ADAPTER_DIR="$HERE/adapters/$(echo "$MODEL" | tr '/:' '__')"

if [[ ! -d "$HERE/.venv" ]]; then
  echo "Creating a local venv in $HERE/.venv ..."
  python3 -m venv "$HERE/.venv"
fi
"$HERE/.venv/bin/python" -c "import mlx_lm" 2>/dev/null || "$HERE/.venv/bin/pip" install --quiet mlx-lm

mkdir -p "$ADAPTER_DIR"
echo "Training LoRA: model=$MODEL iters=$ITERS adapters=$ADAPTER_DIR"
"$HERE/.venv/bin/python" -m mlx_lm lora \
  --model "$MODEL" \
  --train \
  --data "$DATA_DIR" \
  --batch-size 2 \
  --iters "$ITERS" \
  --adapter-path "$ADAPTER_DIR" \
  --save-every 200 \
  --steps-per-report 25 \
  --steps-per-eval 100

echo "Done. Adapter is in: $ADAPTER_DIR"
echo "Bring the whole '$ADAPTER_DIR' folder back and hand it to"
echo "scripts/import_trained_adapter.sh on the original Mac."
SCRIPT
sed -i '' "s|__MODEL__|$MODEL|; s|__ITERS__|$ITERS|" "$BUNDLE/train_standalone.sh"
chmod +x "$BUNDLE/train_standalone.sh"

cat >"$BUNDLE/MANIFEST.md" <<EOF
# Portable training bundle

Generated $(date '+%Y-%m-%d %H:%M') from the Abshaar repo for training
elsewhere on Apple Silicon (e.g. a Harvard Mac Studio).

## What's in here, and why it's rights-safe to carry on a shared machine

- \`dataset/train.jsonl\` ($TRAIN_COUNT examples, sha256 \`$TRAIN_SHA\`)
- \`dataset/valid.jsonl\` ($VALID_COUNT examples, sha256 \`$VALID_SHA\`)

Both files are the output of \`abshaar export-mlx-dataset\`, which only ever
emits \`{"messages": [...]}\` chat examples drawn from trainable corpus
layers. They are already gated by \`export-training-corpus\`'s 8-gram leak
scan against Rafat's copyrighted reference translations (see
\`docs/15_bulleh_shah_expert_model_implementation_plan.md\` Phase 0.3/3).
**Nothing else from the repo is in this bundle**: no private knowledge base,
no Sufinama/PunjabLibrary witness texts, no copyrighted reference
translations, no git history.

## Running the training on the other machine

1. Copy this whole \`portable_bundle\` folder to the Mac Studio (drive,
   AirDrop, whatever's convenient).
2. There, from inside the folder: \`./train_standalone.sh\`
   (defaults to \`$MODEL\`, $ITERS iters — override with two args, e.g.
   \`./train_standalone.sh mlx-community/Qwen3-8B-4bit 600\`).
3. Needs internet access on the Mac Studio to pull mlx-lm (pip) and the base
   model (Hugging Face) on first run.

### On model size, given the extra RAM

The M4 MacBook Air's runbook caps LoRA training at Qwen3-4B (16 GB is
marginal for 8B training). A Mac Studio's much larger unified memory removes
that ceiling — \`mlx-community/Qwen3-8B-4bit\` is a well-grounded next step
since baseline evals for \`qwen3:8b\` already exist in
\`data/processed/training/eval_baseline.md\`, so a tuned 8B adapter compares
directly against an already-measured baseline without redoing Phase 4. Going
further (larger model, bf16 instead of 4-bit) is possible but would need new
baseline rows first — a real decision, not a default to make silently.

## Bringing it back

Bring the entire \`adapters/<model-name>/\` folder back (typically well under
1 GB: LoRA weights only, not the base model). On the original Mac:

    ./scripts/import_trained_adapter.sh /path/to/adapters/<model-name>

That copies it into \`training/adapters/\`, verifies it looks like a real
mlx_lm adapter output, and records its SHA-256 so you can put it in
OFFLOADING/EVAL_MATRIX per the runbook. Then continue from docs/17
Training Runbook §6 (fuse, import to Ollama, acceptance eval) — that part
stays on the machine that will actually *serve* the model.
EOF

echo "Wrote $BUNDLE/ (dataset + train_standalone.sh + MANIFEST.md)"
echo "Copy the whole '$BUNDLE' folder to the target machine."
