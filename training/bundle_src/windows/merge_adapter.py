#!/usr/bin/env python3
"""Merge a trained LoRA adapter into its base model and save the result.

Done on the workstation on purpose: merging needs the full 16 GB base model
in memory, and the workstation already has it downloaded. The merged folder
is the input to GGUF conversion, which is what actually gets carried home
and served with Ollama.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="base model repo id or local path")
    parser.add_argument("--adapter", required=True, help="adapter directory from training")
    parser.add_argument("--out", required=True, help="output directory for the merged model")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"],
                        help="cpu is the safe default; the box has the RAM for it")
    args = parser.parse_args()

    adapter = Path(args.adapter)
    if not adapter.exists():
        print(f"ERROR: adapter directory not found: {adapter}", file=sys.stderr)
        return 1

    out = Path(args.out)
    if out.exists() and any(out.glob("*.safetensors")):
        print(f"Merged model already present at {out}; nothing to do.")
        return 0
    out.mkdir(parents=True, exist_ok=True)

    print(f"Loading base {args.base} on {args.device} ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.base,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
        device_map={"": args.device},
    )
    print(f"Applying adapter {adapter} ...")
    model = PeftModel.from_pretrained(model, str(adapter))
    print("Merging ...")
    model = model.merge_and_unload()

    print(f"Saving merged model to {out} ...")
    model.save_pretrained(str(out), safe_serialization=True, max_shard_size="4GB")

    # The tokenizer saved next to the adapter is the one training used.
    tokenizer_src = str(adapter) if (adapter / "tokenizer_config.json").exists() else args.base
    AutoTokenizer.from_pretrained(tokenizer_src).save_pretrained(str(out))

    meta = {"base_model": args.base, "adapter": str(adapter), "merged": str(out)}
    (out / "abshaar_merge.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Done: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
