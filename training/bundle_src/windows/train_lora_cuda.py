#!/usr/bin/env python3
"""LoRA supervised fine-tune of a Qwen3 base model on the gated Abshaar
Bulleh Shah dataset, for a single NVIDIA GPU on Windows or Linux.

Deliberately built on plain `transformers.Trainer` + `peft` -- no TRL, no
Axolotl, no DeepSpeed, no bitsandbytes on the default path. Those layers
change APIs often and break on Windows; this script only needs torch,
transformers and peft, and every step it takes is visible here.

Loss is computed on the assistant turn only: the prompt tokens are masked
with -100 by comparing the templated prompt against the templated full
conversation and masking their longest common prefix. That works whatever
chat template the tokenizer ships.

Usage:
    python train_lora_cuda.py --model Qwen/Qwen3-8B --data-dir dataset \
        --out-dir runs/qwen3-8b --epochs 3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import Dataset

import transformers
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)

import peft
from peft import LoraConfig, get_peft_model


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def apply_template(tokenizer, messages, add_generation_prompt: bool) -> list[int]:
    """Tokenize a message list with the model's chat template.

    `enable_thinking=False` matters for Qwen3: the default template opens a
    reasoning block, and this dataset contains no reasoning traces. Unknown
    template kwargs are ignored by other templates, but fall back anyway.
    """
    kwargs = dict(
        tokenize=True,
        add_generation_prompt=add_generation_prompt,
        enable_thinking=False,
    )
    try:
        return tokenizer.apply_chat_template(messages, **kwargs)
    except TypeError:
        kwargs.pop("enable_thinking")
        return tokenizer.apply_chat_template(messages, **kwargs)


class ChatSFTDataset(Dataset):
    """{"messages": [system, user, assistant]} -> input_ids + masked labels."""

    def __init__(self, path: Path, tokenizer, max_len: int):
        self.rows: list[dict] = []
        self.truncated = 0
        self.dropped = 0
        self.max_tokens_seen = 0

        for obj in load_jsonl(path):
            messages = obj["messages"]
            if not messages or messages[-1].get("role") != "assistant":
                raise ValueError(f"{path.name}: last message is not an assistant turn")

            full = apply_template(tokenizer, messages, add_generation_prompt=False)
            prompt = apply_template(tokenizer, messages[:-1], add_generation_prompt=True)
            self.max_tokens_seen = max(self.max_tokens_seen, len(full))

            # Longest common prefix = the part that is prompt, not answer.
            prefix = 0
            limit = min(len(full), len(prompt))
            while prefix < limit and full[prefix] == prompt[prefix]:
                prefix += 1

            if len(full) > max_len:
                full = full[:max_len]
                self.truncated += 1

            if prefix >= len(full):
                # Nothing supervised would remain; training on it yields NaN.
                self.dropped += 1
                continue

            labels = [-100] * prefix + full[prefix:]
            self.rows.append({"input_ids": full, "labels": labels})

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, idx: int) -> dict:
        return self.rows[idx]


class PadCollator:
    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, features: list[dict]) -> dict:
        width = max(len(f["input_ids"]) for f in features)
        input_ids, labels, attention = [], [], []
        for f in features:
            pad = width - len(f["input_ids"])
            input_ids.append(f["input_ids"] + [self.pad_id] * pad)
            labels.append(f["labels"] + [-100] * pad)
            attention.append([1] * len(f["input_ids"]) + [0] * pad)
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "attention_mask": torch.tensor(attention, dtype=torch.long),
        }


def build_training_args(**kwargs) -> TrainingArguments:
    """`evaluation_strategy` was renamed `eval_strategy`; support both."""
    try:
        return TrainingArguments(**kwargs)
    except TypeError as exc:
        if "eval_strategy" not in str(exc) and "evaluation_strategy" not in str(exc):
            raise
        renamed = dict(kwargs)
        if "eval_strategy" in renamed:
            renamed["evaluation_strategy"] = renamed.pop("eval_strategy")
        else:
            renamed["eval_strategy"] = renamed.pop("evaluation_strategy")
        return TrainingArguments(**renamed)


def gpu_report() -> dict:
    if not torch.cuda.is_available():
        return {"cuda": False}
    props = torch.cuda.get_device_properties(0)
    return {
        "cuda": True,
        "name": props.name,
        "total_memory_gb": round(props.total_memory / (1024 ** 3), 1),
        "capability": f"{props.major}.{props.minor}",
        "bf16_supported": bool(torch.cuda.is_bf16_supported()),
        "device_count": torch.cuda.device_count(),
    }


# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--data-dir", default="dataset")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=4, help="per-device micro batch")
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-seq-len", type=int, default=4096)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--save-steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", action="store_true", help="continue from the newest checkpoint")
    parser.add_argument("--max-steps", type=int, default=-1, help="debug: stop after N steps")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = data_dir / "train.jsonl"
    valid_path = data_dir / "valid.jsonl"
    for path in (train_path, valid_path):
        if not path.exists():
            print(f"ERROR: missing {path}", file=sys.stderr)
            return 1

    gpu = gpu_report()
    if not gpu["cuda"]:
        print("ERROR: no CUDA device visible to torch. Run 00_bootstrap.ps1 and read its report.", file=sys.stderr)
        return 1

    print(json.dumps({"gpu": gpu}, indent=2))
    set_seed(args.seed)

    tokenizer = AutoTokenizer.from_pretrained(args.model, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Tokenizing {train_path.name} / {valid_path.name} (max_seq_len={args.max_seq_len}) ...")
    train_ds = ChatSFTDataset(train_path, tokenizer, args.max_seq_len)
    valid_ds = ChatSFTDataset(valid_path, tokenizer, args.max_seq_len)
    print(
        f"  train: {len(train_ds)} examples "
        f"(longest {train_ds.max_tokens_seen} tokens, {train_ds.truncated} truncated, {train_ds.dropped} dropped)"
    )
    print(
        f"  valid: {len(valid_ds)} examples "
        f"(longest {valid_ds.max_tokens_seen} tokens, {valid_ds.truncated} truncated, {valid_ds.dropped} dropped)"
    )
    if train_ds.truncated or train_ds.dropped:
        print("  NOTE: raise --max-seq-len if anything was truncated; nothing should be at 4096.")

    use_bf16 = bool(gpu.get("bf16_supported"))
    dtype = torch.bfloat16 if use_bf16 else torch.float16
    print(f"Loading {args.model} in {dtype} ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=dtype,
        attn_implementation="sdpa",   # flash-attn has no reliable Windows wheels
        low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()

    lora = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()
    model.to("cuda")

    checkpoint_dir = out_dir / "checkpoints"
    training_args = build_training_args(
        output_dir=str(checkpoint_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=3,
        bf16=use_bf16,
        fp16=not use_bf16,
        optim="adamw_torch",
        dataloader_num_workers=0,   # Windows: worker spawn is fragile and buys nothing here
        report_to=[],
        seed=args.seed,
        save_safetensors=True,
        remove_unused_columns=False,
        logging_dir=str(out_dir / "logs"),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=valid_ds,
        data_collator=PadCollator(tokenizer.pad_token_id),
    )

    resume = False
    if args.resume and checkpoint_dir.exists():
        resume = any(checkpoint_dir.glob("checkpoint-*"))
        if resume:
            print("Resuming from the newest checkpoint in", checkpoint_dir)

    started = time.time()
    result = trainer.train(resume_from_checkpoint=resume)
    elapsed = time.time() - started

    final_eval = trainer.evaluate()
    print(json.dumps(final_eval, indent=2))

    adapter_dir = out_dir / "adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    adapter_weights = adapter_dir / "adapter_model.safetensors"
    summary = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "base_model": args.model,
        "adapter_dir": str(adapter_dir),
        "adapter_sha256": sha256_file(adapter_weights) if adapter_weights.exists() else None,
        "dataset": {
            "train_path": str(train_path),
            "train_examples": len(train_ds),
            "train_sha256": sha256_file(train_path),
            "valid_examples": len(valid_ds),
            "valid_sha256": sha256_file(valid_path),
            "max_tokens_seen": max(train_ds.max_tokens_seen, valid_ds.max_tokens_seen),
            "truncated": train_ds.truncated + valid_ds.truncated,
            "dropped": train_ds.dropped + valid_ds.dropped,
        },
        "hyperparameters": {
            "epochs": args.epochs,
            "max_steps": args.max_steps,
            "per_device_batch_size": args.batch_size,
            "gradient_accumulation_steps": args.grad_accum,
            "effective_batch_size": args.batch_size * args.grad_accum,
            "learning_rate": args.lr,
            "lr_scheduler": "cosine",
            "max_seq_len": args.max_seq_len,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "precision": "bf16" if use_bf16 else "fp16",
            "seed": args.seed,
        },
        "results": {
            "train_runtime_seconds": round(elapsed, 1),
            "global_steps": int(result.global_step),
            "final_train_loss": result.training_loss,
            "final_eval_loss": final_eval.get("eval_loss"),
            "log_history": trainer.state.log_history,
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "peft": peft.__version__,
            "cuda": torch.version.cuda,
            "gpu": gpu,
        },
    }
    summary_path = out_dir / "train_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("")
    print("=" * 74)
    print(f"Adapter:        {adapter_dir}")
    print(f"Adapter sha256: {summary['adapter_sha256']}")
    print(f"Final eval loss: {final_eval.get('eval_loss')}")
    print(f"Summary:        {summary_path}")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
