#!/usr/bin/env python3
"""Generate answers for the held-out eval set and the honesty probes, with MLX.

This is EVIDENCE, not the project's acceptance evaluation. Acceptance is
`abshaar run-eval` on the serving Mac (judge model + RAG + the rubric in
src/abshaar/evaluate.py). What this produces is a base-vs-tuned pair of
answer files captured on the machine that did the training, so an obviously
broken tune is visible immediately and the scored comparison later has raw
text to point at.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

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


def build_items(data_dir: Path) -> tuple[list[dict], list[dict]]:
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

    eval_items = [
        {
            "id": row.get("id"),
            "task_family": row.get("task_family"),
            "messages": row["messages"][:-1],
            "reference": row["messages"][-1]["content"],
        }
        for row in eval_rows
    ]

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
    return eval_items, probe_items


def render(tokenizer, messages) -> str:
    kwargs = dict(tokenize=False, add_generation_prompt=True, enable_thinking=False)
    try:
        return tokenizer.apply_chat_template(messages, **kwargs)
    except TypeError:
        kwargs.pop("enable_thinking")
        return tokenizer.apply_chat_template(messages, **kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--adapter", default=None, help="adapter dir; omit for the base run")
    parser.add_argument("--data-dir", default="dataset")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--tag", required=True, help="base | tuned")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    from mlx_lm import load, generate

    data_dir = Path(args.data_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    eval_items, probe_items = build_items(data_dir)
    if args.limit:
        eval_items = eval_items[:args.limit]
        probe_items = probe_items[:args.limit]

    print(f"Loading {args.model} ({args.tag}) ...")
    if args.adapter:
        model, tokenizer = load(args.model, adapter_path=args.adapter)
    else:
        model, tokenizer = load(args.model)

    started = time.time()
    for name, items in (("eval", eval_items), ("probes", probe_items)):
        print(f"Generating {name} answers ({len(items)}) ...")
        rows = []
        for index, item in enumerate(items, start=1):
            prompt = render(tokenizer, item["messages"])
            answer = generate(model, tokenizer, prompt=prompt, max_tokens=args.max_tokens, verbose=False)
            record = dict(item)
            record.pop("messages")
            record["question"] = item["messages"][-1]["content"]
            record["answer"] = strip_thinking(answer)
            rows.append(record)
            if index % 10 == 0 or index == len(items):
                print(f"  {index}/{len(items)}", flush=True)

        path = out_dir / f"{args.tag}_{name}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Wrote {path} ({len(rows)} rows)")

    print(f"Done in {time.time() - started:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
