#!/usr/bin/env bash
# Fuse the LoRA adapter into the base weights, and export GGUF when possible.
#
# GGUF is what Ollama serves, and Ollama is what the project's eval harness
# talks to. It can only be produced from a NON-quantised fuse: if you trained
# on a 4-bit base (the memory-safe default) the fused model is quantised MLX
# and llama.cpp cannot read it. This script says which case you are in rather
# than failing obscurely.
#
# Usage: ./02_fuse_export.sh [-r work_root] [-m model_repo] [--skip-gguf]

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

ROOT_ARG=""
MODEL="mlx-community/Qwen3-8B-4bit"
TAG=""
QUANT="Q4_K_M"
SKIP_GGUF=0
while [ $# -gt 0 ]; do
    case "$1" in
        -r|--root)  ROOT_ARG="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        -t|--tag)   TAG="$2"; shift 2 ;;
        -q|--quant) QUANT="$2"; shift 2 ;;
        --skip-gguf) SKIP_GGUF=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

init_env "$(resolve_root "$ROOT_ARG")"
require_venv

SLUG="$(run_slug "$MODEL")"
[ -n "$TAG" ] && SLUG="$SLUG-$TAG"
RUN_DIR="$ROOT/runs/$SLUG"
ADAPTER_DIR="$RUN_DIR/adapter"
FUSED_DIR="$RUN_DIR/fused"
[ -d "$ADAPTER_DIR" ] || { echo "ERROR: no adapter at $ADAPTER_DIR -- run ./01_train.sh first." >&2; exit 1; }

head_ "Fusing adapter into base weights"
mlx_run fuse --model "$MODEL" --adapter-path "$ADAPTER_DIR" --save-path "$FUSED_DIR"
note_ "Fused model: $FUSED_DIR ($(dir_gb "$FUSED_DIR") GB)"

[ "$SKIP_GGUF" = "1" ] && { note_ "--skip-gguf set; stopping after the fuse."; exit 0; }

IS_QUANTIZED=$("$PY" - "$FUSED_DIR" <<'PYQ'
import json, sys
from pathlib import Path
config = json.loads((Path(sys.argv[1]) / "config.json").read_text(encoding="utf-8"))
print("yes" if config.get("quantization") or config.get("quantization_config") else "no")
PYQ
)

head_ "GGUF export"
if [ "$IS_QUANTIZED" = "yes" ]; then
    warn_ "The fused model is quantised MLX, which llama.cpp cannot convert."
    note_ "You still have: a fused MLX model that mlx_lm can serve, and the adapter."
    note_ "For an Ollama-servable GGUF, retrain from a non-quantised base on a Mac"
    note_ "with the memory for it, e.g. -m mlx-community/Qwen3-8B-bf16 (needs ~32 GB+)."
    exit 0
fi

TOOLS="$ROOT/tools"
mkdir -p "$TOOLS"
if [ ! -d "$TOOLS/llama.cpp" ]; then
    note_ "Cloning llama.cpp (shallow) for its converter ..."
    git clone --depth 1 https://github.com/ggml-org/llama.cpp "$TOOLS/llama.cpp"
fi
"$PY" -m pip install --quiet gguf torch numpy sentencepiece protobuf

OUT_DIR="$ROOT/outbox/model"
mkdir -p "$OUT_DIR"
NAME="abshaar-bulleh-$(printf '%s' "$SLUG" | tr 'A-Z' 'a-z')"
F16="$OUT_DIR/$NAME.f16.gguf"

if [ ! -f "$F16" ]; then
    "$PY" "$TOOLS/llama.cpp/convert_hf_to_gguf.py" "$FUSED_DIR" --outfile "$F16" --outtype f16
fi

QUANT_BIN="$(command -v llama-quantize || true)"
if [ -z "$QUANT_BIN" ] && [ -x "$TOOLS/llama.cpp/build/bin/llama-quantize" ]; then
    QUANT_BIN="$TOOLS/llama.cpp/build/bin/llama-quantize"
fi
if [ -n "$QUANT_BIN" ]; then
    LOWER="$(printf '%s' "$QUANT" | tr 'A-Z' 'a-z')"
    "$QUANT_BIN" "$F16" "$OUT_DIR/$NAME.$LOWER.gguf" "$QUANT"
    rm -f "$F16"
    note_ "GGUF: $OUT_DIR/$NAME.$LOWER.gguf"
else
    warn_ "No llama-quantize found (brew install llama.cpp, or build $TOOLS/llama.cpp)."
    note_ "Keeping the f16 GGUF: $F16 -- Ollama can serve it, it is just large."
fi

GGUF_NAME="$(cd "$OUT_DIR" && ls *.gguf 2>/dev/null | head -1)"
cat > "$OUT_DIR/Modelfile.abshaar-bulleh" <<EOF
# Ollama Modelfile for the tuned Bulleh Shah model.
# From the folder holding this file and the .gguf:
#   ollama create abshaar-bulleh -f Modelfile.abshaar-bulleh
FROM ./$GGUF_NAME
PARAMETER temperature 0.6
PARAMETER top_p 0.95
SYSTEM """You are Abshaar, a scholarly assistant on the Punjabi Sufi poet Bulleh Shah. Answer from your studied corpus. Preserve uncertainty and dispute qualifiers exactly; when the corpus does not contain an answer, say so plainly instead of guessing."""
EOF
note_ "Modelfile: $OUT_DIR/Modelfile.abshaar-bulleh"
note_ "Next: ./03_generate.sh -r \"$ROOT\" -m $MODEL"
