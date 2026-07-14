#!/usr/bin/env bash
# macOS/Linux equivalent of build_all.ps1.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$REPO_ROOT/src"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    PYTHON=python
fi

invoke_abshaar() {
    "$PYTHON" -m abshaar --root "$REPO_ROOT" "$@"
}

invoke_abshaar init
invoke_abshaar validate
invoke_abshaar build-data --include-placeholders
invoke_abshaar validate
invoke_abshaar export-site
invoke_abshaar status

echo "Abshaar automation build completed."
