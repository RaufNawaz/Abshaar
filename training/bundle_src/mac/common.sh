#!/usr/bin/env bash
# Shared helpers for the Abshaar Apple Silicon bundle.
# Written for macOS's default bash 3.2 -- no associative arrays, no ${x,,}.

set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

head_() { printf '\n%s\n%s\n%s\n' "$(printf '=%.0s' $(seq 1 74))" "$1" "$(printf '=%.0s' $(seq 1 74))"; }
note_() { printf '  %s\n' "$1"; }
warn_() { printf '  WARNING: %s\n' "$1" >&2; }

# The work root holds everything: venv, model cache, adapters, outbox. One
# folder is the whole session, which is what a shared or wiped machine needs.
resolve_root() {
    local root="${1:-${ABSHAAR_ROOT:-$BUNDLE_DIR}}"
    mkdir -p "$root"
    (cd "$root" && pwd)
}

init_env() {
    ROOT="$1"
    export ABSHAAR_ROOT="$ROOT"
    export HF_HOME="$ROOT/cache/huggingface"
    export PIP_CACHE_DIR="$ROOT/cache/pip"
    export PYTHONUTF8=1
    mkdir -p "$ROOT/cache" "$ROOT/logs" "$ROOT/outbox" "$ROOT/downloads" "$ROOT/.stages"
    PY="$ROOT/venv/bin/python"
}

stage_done()  { [ -f "$ROOT/.stages/$1" ]; }
stage_mark()  { date +%Y-%m-%dT%H:%M:%S > "$ROOT/.stages/$1"; }

require_venv() {
    if [ ! -x "$PY" ]; then
        echo "ERROR: no venv at $PY -- run ./00_bootstrap.sh first." >&2
        exit 1
    fi
}

# mlx-lm moved its entry points between releases; try the current form first.
mlx_run() {
    local sub="$1"; shift
    if "$PY" -m mlx_lm "$sub" "$@"; then
        return 0
    fi
    echo "(falling back to python -m mlx_lm.$sub)" >&2
    "$PY" -m "mlx_lm.$sub" "$@"
}

run_slug() { printf '%s' "$1" | tr '/:' '__'; }

free_gb() { df -g "$1" 2>/dev/null | awk 'NR==2{print $4}'; }
dir_gb()  { if [ -d "$1" ]; then du -sg "$1" 2>/dev/null | awk '{print $1}'; else echo 0; fi; }
