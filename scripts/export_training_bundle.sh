#!/usr/bin/env bash
# Packages the gated, leak-scanned training dataset plus a complete
# standalone training toolchain into shippable bundles for another machine:
#
#   mac      -> Apple Silicon / mlx-lm      (a Mac Studio, or this Air)
#   windows  -> Windows + NVIDIA / PyTorch  (the Threadripper workstation)
#
# What deliberately does NOT travel: the private knowledge base, the
# Sufinama/PunjabLibrary witness texts, Rafat's copyrighted reference
# translations, git history. Only the gated dataset goes onto a shared or
# lab machine.
#
# Usage (from the repo root):
#   ./scripts/export_training_bundle.sh                       # both bundles
#   ./scripts/export_training_bundle.sh --target windows
#   ./scripts/export_training_bundle.sh --mac-model mlx-community/Qwen3-4B-4bit
#   ./scripts/export_training_bundle.sh <mac_model> <iters>   # legacy positional form
#
# Outputs (gitignored build artefacts) under training/dist/:
#   <target>/                      the unpacked bundle
#   abshaar_<target>_bundle.zip    the same thing, zipped
#   abshaar_<target>_bundle.zip.b64.txt   email-safe encoding (see EMAIL_ME.md)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

TARGET="both"
MAC_MODEL="mlx-community/Qwen3-8B-4bit"
CUDA_MODEL="Qwen/Qwen3-8B"
ITERS=600
MAKE_ZIP=1

# Legacy positional form: export_training_bundle.sh [mac_model] [iters]
if [ $# -gt 0 ] && [ "${1#-}" = "$1" ]; then
    MAC_MODEL="$1"; shift
    if [ $# -gt 0 ] && [ "${1#-}" = "$1" ]; then ITERS="$1"; shift; fi
fi
while [ $# -gt 0 ]; do
    case "$1" in
        --target)     TARGET="$2"; shift 2 ;;
        --mac-model)  MAC_MODEL="$2"; shift 2 ;;
        --cuda-model) CUDA_MODEL="$2"; shift 2 ;;
        --iters)      ITERS="$2"; shift 2 ;;
        --no-zip)     MAKE_ZIP=0; shift ;;
        -h|--help)    sed -n '2,25p' "$0"; exit 0 ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done
case "$TARGET" in mac|windows|both) ;; *) echo "--target must be mac, windows or both" >&2; exit 2 ;; esac

DATA_SRC="data/processed/training"
MLX_SRC="$DATA_SRC/mlx"
for f in "$MLX_SRC/train.jsonl" "$MLX_SRC/valid.jsonl" "$DATA_SRC/eval.jsonl" "$DATA_SRC/probes.jsonl"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: $f missing; run ./scripts/abshaar.sh export-mlx-dataset first." >&2
        exit 1
    fi
done

DIST="training/dist"
mkdir -p "$DIST"

sha_of()   { shasum -a 256 "$1" | awk '{print $1}'; }
count_of() { grep -c . "$1" | tr -d ' '; }

TRAIN_N="$(count_of "$MLX_SRC/train.jsonl")";  TRAIN_SHA="$(sha_of "$MLX_SRC/train.jsonl")"
VALID_N="$(count_of "$MLX_SRC/valid.jsonl")";  VALID_SHA="$(sha_of "$MLX_SRC/valid.jsonl")"
EVAL_N="$(count_of "$DATA_SRC/eval.jsonl")";   EVAL_SHA="$(sha_of "$DATA_SRC/eval.jsonl")"
PROBE_N="$(count_of "$DATA_SRC/probes.jsonl")"; PROBE_SHA="$(sha_of "$DATA_SRC/probes.jsonl")"

write_manifest() {
    local bundle="$1" platform="$2" model="$3" runline="$4"
    cat >"$bundle/MANIFEST.md" <<EOF
# Abshaar training bundle — $platform

Generated $(date '+%Y-%m-%d %H:%M') from the Abshaar repository
(commit \`$(git rev-parse --short HEAD 2>/dev/null || echo unknown)\`, branch \`$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)\`).

Default base model for this bundle: \`$model\`

## Dataset (the only corpus material in here)

| File | Examples | SHA-256 |
|---|---|---|
| \`dataset/train.jsonl\` | $TRAIN_N | \`$TRAIN_SHA\` |
| \`dataset/valid.jsonl\` | $VALID_N | \`$VALID_SHA\` |
| \`dataset/eval.jsonl\` | $EVAL_N | \`$EVAL_SHA\` |
| \`dataset/probes.jsonl\` | $PROBE_N | \`$PROBE_SHA\` |

\`train.jsonl\` and \`valid.jsonl\` are the output of \`abshaar export-mlx-dataset\`:
\`{"messages": [...]}\` chat examples drawn only from corpus layers marked
trainable, gated by \`export-training-corpus\`'s 8-gram leak scan against
Rafat's copyrighted reference translations (plan Phase 0.3/3).
\`eval.jsonl\` is the held-out split from the same generator — its work
clusters are disjoint from training — and \`probes.jsonl\` is the fixed
honesty/disputed-fact probe set built from it.

**Nothing else from the repository is here:** no private knowledge base, no
Sufinama or PunjabLibrary witness texts, no reference translations, no git
history. Keep it that way — this is what makes the bundle safe to carry onto
a shared or institutional machine.

## Running it

$runline

Read \`$([ "$platform" = "Windows / NVIDIA CUDA" ] && echo README_WINDOWS.md || echo README_MAC.md)\` first — especially the section on
copying results off the machine before you sign out.

## Bringing it back

The pack stage leaves \`abshaar_results_small.zip\` (adapter + summaries +
generations + logs) and, when one was produced, a GGUF under
\`outbox/model/\`. In the repository:

    ./scripts/import_trained_adapter.sh /path/to/outbox/adapter/<model-slug>

then continue from \`docs/17_training_runbook.md\` §6 (serve → acceptance
eval). Full round trip: \`docs/18_workstation_training_runbook.md\`.
EOF
}

copy_dataset() {
    local bundle="$1"
    mkdir -p "$bundle/dataset"
    cp "$MLX_SRC/train.jsonl"     "$bundle/dataset/train.jsonl"
    cp "$MLX_SRC/valid.jsonl"     "$bundle/dataset/valid.jsonl"
    cp "$DATA_SRC/eval.jsonl"     "$bundle/dataset/eval.jsonl"
    cp "$DATA_SRC/probes.jsonl"   "$bundle/dataset/probes.jsonl"
}

package() {
    local name="$1"
    local bundle="$DIST/$name"
    if [ "$MAKE_ZIP" = "0" ]; then return 0; fi
    local zip_path="$DIST/abshaar_${name}_bundle.zip"
    rm -f "$zip_path" "$zip_path.b64.txt"
    ( cd "$DIST" && zip -qr "abshaar_${name}_bundle.zip" "$name" )
    # Mail providers block .ps1/.cmd/.py attachments, including inside a ZIP.
    # The base64 text file is the copy that survives an email round trip.
    base64 < "$zip_path" > "$zip_path.b64.txt"
    printf '  %s (%s)\n' "$zip_path" "$(du -h "$zip_path" | awk '{print $1}')"
    printf '  %s (%s)\n' "$zip_path.b64.txt" "$(du -h "$zip_path.b64.txt" | awk '{print $1}')"
}

if [ "$TARGET" = "mac" ] || [ "$TARGET" = "both" ]; then
    BUNDLE="$DIST/mac"
    rm -rf "$BUNDLE"; mkdir -p "$BUNDLE"
    cp training/bundle_src/mac/*.sh training/bundle_src/mac/*.py \
       training/bundle_src/mac/requirements-mlx.txt training/bundle_src/mac/README_MAC.md "$BUNDLE/"
    chmod +x "$BUNDLE"/*.sh
    copy_dataset "$BUNDLE"
    write_manifest "$BUNDLE" "Apple Silicon / MLX" "$MAC_MODEL" \
"    chmod +x *.sh
    ./run_all.sh -r ~/abshaar-work -m $MAC_MODEL -i $ITERS"
    echo "Wrote $BUNDLE/"
    package mac
fi

if [ "$TARGET" = "windows" ] || [ "$TARGET" = "both" ]; then
    BUNDLE="$DIST/windows"
    rm -rf "$BUNDLE"; mkdir -p "$BUNDLE"
    cp training/bundle_src/windows/*.ps1 training/bundle_src/windows/*.py \
       training/bundle_src/windows/RUN_ALL.cmd training/bundle_src/windows/requirements-cuda.txt \
       training/bundle_src/windows/README_WINDOWS.md "$BUNDLE/"
    # Ship the Windows scripts with CRLF whatever this checkout happens to hold:
    # .gitattributes normalises them on a Windows checkout, but the bundle is
    # built on the Mac, and cmd.exe is the fussy one about bare LF.
    for f in "$BUNDLE"/*.ps1 "$BUNDLE"/*.cmd; do
        [ -f "$f" ] || continue
        perl -pi -e 's/\r?\n/\r\n/' "$f"
    done
    copy_dataset "$BUNDLE"
    write_manifest "$BUNDLE" "Windows / NVIDIA CUDA" "$CUDA_MODEL" \
"    Double-click RUN_ALL.cmd, or in PowerShell:
    powershell -NoProfile -ExecutionPolicy Bypass -File .\\RUN_ALL.ps1 -Root D:\\abshaar-work"
    echo "Wrote $BUNDLE/"
    package windows
fi

cat >"$DIST/EMAIL_ME.md" <<'EOF'
# Getting these bundles onto the other machine

Two copies of each bundle are produced:

| File | Use it when |
|---|---|
| `abshaar_<target>_bundle.zip` | USB drive, Google Drive, iCloud, Slack, AirDrop — anything that is not email. Unzip and go. |
| `abshaar_<target>_bundle.zip.b64.txt` | **Email.** Gmail and most corporate mail filters block `.ps1`, `.cmd` and `.py` attachments *even inside a ZIP*, and reject the whole message. A `.txt` file always gets through. |

## Decoding the .txt on the other machine

**Windows** (built-in, no install):

```cmd
certutil -decode abshaar_windows_bundle.zip.b64.txt abshaar_windows_bundle.zip
```

Then right-click the ZIP → Extract All. In PowerShell instead:

```powershell
Expand-Archive .\abshaar_windows_bundle.zip -DestinationPath .
```

**macOS / Linux:**

```bash
base64 -D -i abshaar_mac_bundle.zip.b64.txt -o abshaar_mac_bundle.zip   # macOS
base64 -d  abshaar_mac_bundle.zip.b64.txt > abshaar_mac_bundle.zip      # Linux
unzip abshaar_mac_bundle.zip
chmod +x mac/*.sh
```

Verify it arrived intact by comparing the ZIP's checksum with the one printed
when the bundle was built (`shasum -a 256` on the Mac, `certutil -hashfile
<file> SHA256` on Windows).

## Then

- Windows workstation: open `windows/README_WINDOWS.md`, run `RUN_ALL.cmd`.
- Apple Silicon Mac: open `mac/README_MAC.md`, run `./run_all.sh`.

Both READMEs start with the same warning: the machine may be wiped when you
sign out, so the last stage packs everything you must copy off.
EOF

echo ""
echo "Checksums of the shippable archives:"
for f in "$DIST"/*.zip; do [ -f "$f" ] && shasum -a 256 "$f"; done
echo ""
echo "See $DIST/EMAIL_ME.md for how to move these to the other machine."
