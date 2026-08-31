#!/usr/bin/env python3
"""Generate answers for the held-out eval set and the honesty probes.

This is EVIDENCE, not the project's acceptance evaluation. Acceptance is
`abshaar run-eval` on the Mac (judge model + RAG + the scoring rubric in
src/abshaar/evaluate.py). What this gives you is a base-vs-tuned pair of
answer files captured on the machine that did the training -- so if the
tuned model is producing garbage you find out before you sign out and lose
the GPU, and so the scored comparison later has raw text to point at.

Greedy decoding (do_sample=False) so base and tuned are compared on equal,
reproducible terms.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def strip_thinking(text: str) -> str:
    return THINK_RE.sub("", text).replace("<think>", "").replace("</think>", "").strip()


def build_items(data_dir: Path) -> tuple[list[dict], list[dict], str]:
    """Return (eval items, probe items, system prompt)."""
    eval_rows = load_jsonl(data_dir / "eval.jsonl")
    probe_rows = load_jsonl(data_dir / "probes.jsonl")

    system = ""
    for row in eval_rows:
        for message in row.get("messages", []):
            if message.get("role") == "system":
                system = message["content"]
                break
        if system:
            break

    eval_items = []
    for row in eval_rows:
        messages = row["messages"]
        eval_items.append({
            "id": row.get("id"),
            "task_family": row.get("task_family"),
            "messages": messages[:-1],
            "reference": messages[-1]["content"],
        })

    probe_items = []
    for row in probe_rows:
        messages = [{"role": "user", "content": row["question"]}]
        if system:
            messages.insert(0, {"role": "system", "content": system})
        probe_items.append({
            "id": row.get("id"),
            "category": row.get("category"),
            "task_family": row.get("task_family"),
            "messages": messages,
            "reference": row.get("reference", ""),
        })

    return eval_items, probe_items, system


def render(tokenizer, messages) -> str:
    kwargs = dict(tokenize=False, add_generation_prompt=True, enable_thinking=False)
    try:
        return tokenizer.apply_chat_template(messages, **kwargs)
    except TypeError:
        kwargs.pop("enable_thinking")
        return tokenizer.apply_chat_template(messages, **kwargs)


def generate_all(model, tokenizer, items: list[dict], max_new_tokens: int, batch_size: int) -> list[dict]:
    results = []
    for start in range(0, len(items), batch_size):
        batch = items[start:start + batch_size]
        prompts = [render(tokenizer, item["messages"]) for item in batch]
        encoded = tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            output = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        for item, prompt_ids, out_ids in zip(batch, encoded["input_ids"], output):
            answer = tokenizer.decode(out_ids[len(prompt_ids):], skip_special_tokens=True)
            record = dict(item)
            record.pop("messages")
            record["question"] = item["messages"][-1]["content"]
            record["answer"] = strip_thinking(answer)
            results.append(record)
        done = min(start + batch_size, len(items))
        print(f"  {done}/{len(items)}", flush=True)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="base model repo id or local path")
    parser.add_argument("--adapter", default=None, help="LoRA adapter dir; omit for the base run")
    parser.add_argument("--data-dir", default="dataset")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--tag", required=True, help="base | tuned")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="debug: only the first N items")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    eval_items, probe_items, _ = build_items(data_dir)
    if args.limit:
        eval_items = eval_items[:args.limit]
        probe_items = probe_items[:args.limit]

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"   # required for batched generation

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    print(f"Loading {args.model} ({args.tag}) ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, attn_implementation="sdpa", low_cpu_mem_usage=True,
    )
    if args.adapter:
        from peft import PeftModel
        print(f"Applying adapter {args.adapter} ...")
        model = PeftModel.from_pretrained(model, args.adapter)
    model.to("cuda")
    model.eval()

    started = time.time()
    print(f"Generating eval answers ({len(eval_items)}) ...")
    eval_out = generate_all(model, tokenizer, eval_items, args.max_new_tokens, args.batch_size)
    print(f"Generating probe answers ({len(probe_items)}) ...")
    probe_out = generate_all(model, tokenizer, probe_items, args.max_new_tokens, args.batch_size)

    for name, rows in (("eval", eval_out), ("probes", probe_out)):
        path = out_dir / f"{args.tag}_{name}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Wrote {path} ({len(rows)} rows)")

    mean_len = sum(len(r["answer"]) for r in eval_out) / max(len(eval_out), 1)
    print(f"Mean eval answer length: {mean_len:.0f} chars; {time.time() - started:.0f}s total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
