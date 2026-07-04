#!/usr/bin/env bash
# macOS/Linux equivalent of abshaar.ps1.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$REPO_ROOT/src"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    PYTHON=python
fi

exec "$PYTHON" -m abshaar --root "$REPO_ROOT" "$@"
