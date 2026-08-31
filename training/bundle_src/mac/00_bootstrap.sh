#!/usr/bin/env bash
# Installs everything the training run needs, into one folder.
#
# Creates a venv, installs mlx-lm, and pre-downloads the base model into the
# bundle's own Hugging Face cache -- nothing goes into ~/.cache, so on a
# shared or wiped machine this one folder is the entire session.
#
# Usage: ./00_bootstrap.sh [-r work_root] [-m model_repo] [--skip-model]

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

ROOT_ARG=""
MODEL="mlx-community/Qwen3-8B-4bit"
SKIP_MODEL=0
while [ $# -gt 0 ]; do
    case "$1" in
        -r|--root)  ROOT_ARG="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        --skip-model) SKIP_MODEL=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

init_env "$(resolve_root "$ROOT_ARG")"

head_ "Abshaar bootstrap - work root: $ROOT"
note_ "Everything (venv, model cache, adapters, results) lives under this folder."

if [ "$(uname -m)" != "arm64" ]; then
    warn_ "This is not an Apple Silicon Mac ($(uname -m)). MLX will not work here."
    warn_ "Use the Windows/CUDA bundle instead, or a different machine."
    exit 1
fi
note_ "Machine: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo 'unknown')"
note_ "Memory:  $(( $(sysctl -n hw.memsize) / 1073741824 )) GB unified"
note_ "Free disk: $(free_gb "$ROOT") GB"

head_ "1/3  Python"
BASE_PY=""
for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        version="$("$candidate" -c 'import sys;print("%d.%d" % sys.version_info[:2])')"
        major="${version%%.*}"; minor="${version##*.}"
        if [ "$major" = "3" ] && [ "$minor" -ge 9 ]; then BASE_PY="$candidate"; break; fi
    fi
done
if [ -z "$BASE_PY" ]; then
    echo "ERROR: no Python 3.9+ found. Install one (python.org or 'brew install python@3.12') and re-run." >&2
    exit 1
fi
note_ "Using $BASE_PY ($("$BASE_PY" --version 2>&1))"

head_ "2/3  Virtual environment and mlx-lm"
if [ ! -x "$PY" ]; then
    "$BASE_PY" -m venv "$ROOT/venv"
fi
if stage_done deps; then
    note_ "Already installed (rm $ROOT/.stages/deps to force a reinstall)."
else
    "$PY" -m pip install --quiet --upgrade pip wheel setuptools
    "$PY" -m pip install -r "$BUNDLE_DIR/requirements-mlx.txt"
    stage_mark deps
fi
"$PY" - <<'PYCHECK'
import json, platform, sys
report = {"python": sys.version.split()[0], "platform": platform.platform()}
import mlx.core as mx
import mlx_lm
report["mlx"] = mx.__version__
report["mlx_lm"] = getattr(mlx_lm, "__version__", "unknown")
print(json.dumps(report, indent=2))
PYCHECK

head_ "3/3  Base model: $MODEL"
if [ "$SKIP_MODEL" = "1" ]; then
    note_ "--skip-model set; not downloading weights."
elif stage_done "model_$(run_slug "$MODEL")"; then
    note_ "Already downloaded (cache: $HF_HOME)."
else
    HF_HUB_ENABLE_HF_TRANSFER=1 "$PY" - "$MODEL" <<'PYDL'
import os, sys
if os.environ.get("HF_HUB_ENABLE_HF_TRANSFER") == "1":
    try:
        import hf_transfer  # noqa: F401
    except Exception:
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
from huggingface_hub import snapshot_download
path = snapshot_download(repo_id=sys.argv[1], ignore_patterns=["*.pth", "*.gguf", "original/*"])
print("Model files are in:", path)
PYDL
    stage_mark "model_$(run_slug "$MODEL")"
fi
note_ "Model cache size: $(dir_gb "$HF_HOME") GB"

head_ "Bootstrap complete"
note_ "Next: ./01_train.sh -r \"$ROOT\" -m $MODEL"
