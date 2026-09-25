#!/usr/bin/env bash
# Serve a trained LoRA adapter through mlx_lm's OpenAI-compatible server, so it
# can be reached by `abshaar ask --model mlx:<label>` -- i.e. behind retrieval
# and the citation gate.
#
# That framing is deliberate. Served bare on 2026-09-24, run 2's adapter
# invented two sources and attributed them to the archive (see
# training/EVAL_MATRIX.md). Retrieval plus the citation gate is the thing that
# makes it usable; this script exists to put it there, not to expose it raw.
#
#   ./scripts/serve_tuned.sh              # run 2 (default)
#   ./scripts/serve_tuned.sh run1         # run 1's adapter
#   ./scripts/serve_tuned.sh base         # base weights, no adapter
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHICH="${1:-run2}"
PORT="${PORT:-8080}"
BASE="mlx-community/Qwen3-8B-4bit"

case "$WHICH" in
  run2) ADAPTER="$ROOT/training/adapters/mlx-community_Qwen3-8B-4bit-run2" ;;
  run1) ADAPTER="$ROOT/training/adapters/mlx-community_Qwen3-8B-4bit" ;;
  base) ADAPTER="" ;;
  *) echo "unknown target '$WHICH' (expected run1, run2 or base)" >&2; exit 2 ;;
esac

if [ -n "$ADAPTER" ]; then
  [ -f "$ADAPTER/adapters.safetensors" ] || { echo "no adapter at $ADAPTER" >&2; exit 1; }
  echo "serving $BASE + $WHICH adapter on port $PORT"
  echo "  adapter sha256: $(shasum -a 256 "$ADAPTER/adapters.safetensors" | cut -d' ' -f1)"
  exec "$ROOT/.venv/bin/python" -m mlx_lm server \
    --model "$BASE" --adapter-path "$ADAPTER" --port "$PORT" --log-level WARNING
else
  echo "serving $BASE with NO adapter on port $PORT"
  exec "$ROOT/.venv/bin/python" -m mlx_lm server \
    --model "$BASE" --port "$PORT" --log-level WARNING
fi
