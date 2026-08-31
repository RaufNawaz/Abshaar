#!/usr/bin/env python3
"""Pre-download a base model into the bundle's own Hugging Face cache.

Separate from training on purpose: on a workstation that wipes itself at
sign-out this is the one slow step (~16 GB for an 8B model), and it should
be restartable on its own without touching anything else. huggingface_hub
resumes partial downloads, so re-running after a dropped connection is safe.
"""

from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Hugging Face repo id, e.g. Qwen/Qwen3-8B")
    args = parser.parse_args()

    # hf_transfer makes big downloads several times faster, but it is an
    # optional native dependency; fall back rather than fail the whole run.
    if os.environ.get("HF_HUB_ENABLE_HF_TRANSFER") == "1":
        try:
            import hf_transfer  # noqa: F401
        except Exception:
            print("hf_transfer not importable; falling back to the standard downloader.")
            os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

    from huggingface_hub import snapshot_download

    print(f"Downloading {args.model} into {os.environ.get('HF_HOME', '(default cache)')} ...")
    path = snapshot_download(
        repo_id=args.model,
        ignore_patterns=["*.pth", "*.gguf", "original/*", "*.msgpack", "*.h5"],
        max_workers=8,
    )
    print(f"Model files are in: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
