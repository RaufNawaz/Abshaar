#!/usr/bin/env bash
# Collect everything worth keeping into <root>/outbox, checksum it, and zip
# the small artefacts into one file you can email or upload.
#
# On a shared or wiped machine, anything not copied off before you log out is
# gone -- including the compute that produced it.
#
# Usage: ./04_pack_outbox.sh [-r work_root] [-m model_repo]

. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

ROOT_ARG=""
MODEL="mlx-community/Qwen3-8B-4bit"
while [ $# -gt 0 ]; do
    case "$1" in
        -r|--root)  ROOT_ARG="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

init_env "$(resolve_root "$ROOT_ARG")"

SLUG="$(run_slug "$MODEL")"
RUN_DIR="$ROOT/runs/$SLUG"
OUTBOX="$ROOT/outbox"

head_ "Packing results"
if [ -d "$RUN_DIR/adapter" ]; then
    mkdir -p "$OUTBOX/adapter/$SLUG"
    cp -R "$RUN_DIR/adapter/." "$OUTBOX/adapter/$SLUG/"
    note_ "adapter -> $OUTBOX/adapter/$SLUG"
else
    warn_ "No adapter in $RUN_DIR -- nothing trained?"
fi
[ -f "$RUN_DIR/train_summary.json" ] && cp "$RUN_DIR/train_summary.json" "$OUTBOX/"
if [ -d "$ROOT/logs" ]; then mkdir -p "$OUTBOX/logs" && cp -R "$ROOT/logs/." "$OUTBOX/logs/"; fi

( cd "$OUTBOX" && find . -type f ! -name 'SHA256SUMS.txt' -print0 | xargs -0 shasum -a 256 > SHA256SUMS.txt )
note_ "SHA256SUMS.txt ($(wc -l < "$OUTBOX/SHA256SUMS.txt" | tr -d ' ') files)"

# One small zip: everything except the multi-GB model directory.
ZIP="$ROOT/abshaar_results_small.zip"
rm -f "$ZIP"
( cd "$OUTBOX" && zip -qr "$ZIP" . -x 'model/*' )
note_ "$ZIP ($(du -h "$ZIP" | awk '{print $1}'))"

head_ "BEFORE YOU LOG OUT OF THIS MACHINE"
echo ""
echo "  1. Copy this ZIP off the machine (AirDrop, drive, upload, or email):"
echo "       $ZIP"
if [ -d "$OUTBOX/model" ]; then
    for f in "$OUTBOX/model"/*.gguf; do
        [ -f "$f" ] || continue
        echo "  2. Copy the servable model by hand ($(du -h "$f" | awk '{print $1}') -- too big to email):"
        echo "       $f"
    done
else
    echo "  2. No GGUF was produced (see 02_fuse_export.sh's output for why)."
    echo "     The adapter in the ZIP is the reproducible artefact; fusing again"
    echo "     elsewhere means re-downloading the base model."
fi
echo "  3. Verify the copy: shasum -c SHA256SUMS.txt in the unpacked folder."
echo "  4. Only then log out."
echo ""
