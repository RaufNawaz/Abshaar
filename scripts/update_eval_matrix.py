#!/usr/bin/env python3
"""Fill training/EVAL_MATRIX.md's acceptance table from the eval run files.

The numbers in that table decide whether run 2 ships. Typing them by hand from
a log is exactly the kind of step that puts a wrong number in a document and
leaves it there, so this reads `data/processed/training/eval_runs/*.json` and
writes the rows, refusing to invent anything for a run that has not happened.

    ./.venv/bin/python scripts/update_eval_matrix.py [--check]

--check exits non-zero if the table does not match the run files, so a stale
table fails loudly rather than being believed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data/processed/training/eval_runs"
MATRIX = ROOT / "training/EVAL_MATRIX.md"

# (row label, eval-run file stem). The four rows the acceptance criterion needs.
ROWS = [
    ("`qwen3:8b` base", "qwen3_8b"),
    ("`qwen3:8b` + RAG", "qwen3_8b_rag"),
    ("tuned (run 2)", "mlx_run2"),
    ("tuned (run 2) + RAG", "mlx_run2_rag"),
]

START = "| Model | factual | honesty | notes |"
CRITERION = "**Acceptance criterion"


def load(stem: str) -> dict | None:
    path = RUNS / f"{stem}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))["summary"]


def build_table() -> tuple[str, list[str]]:
    lines = [START, "|---|---|---|---|"]
    missing = []
    for label, stem in ROWS:
        summary = load(stem)
        if summary is None:
            missing.append(stem)
            lines.append(f"| {label} | — | — | not run |")
            continue
        note = f"{summary['probes']} probes, judge {summary['judge']}"
        judge_failures = summary.get("judge_failures") or 0
        if judge_failures:
            # A partially-judged run must never read as a clean one.
            note += f", **{judge_failures} judge failures (degraded to token-F1)**"
        answer_failures = summary.get("answer_failures") or 0
        if answer_failures:
            # An empty answer still scores, so an unmarked run would understate
            # the model rather than admit the probe never got an answer.
            note += f", **{answer_failures} probes got no answer (scored 0)**"
        lines.append(
            f"| {label} | {summary['factual']} | {summary['honesty']} | {note} |"
        )
    return "\n".join(lines), missing


def verdict() -> str:
    base_rag, tuned_rag = load("qwen3_8b_rag"), load("mlx_run2_rag")
    base, tuned = load("qwen3_8b"), load("mlx_run2")
    if not all([base_rag, tuned_rag, base, tuned]):
        return (
            "\n\n**Verdict: cannot be computed yet** — one or more runs is missing "
            "above. The criterion needs all four.\n"
        )
    factual_ok = tuned_rag["factual"] >= base_rag["factual"]
    honesty_ok = tuned["honesty"] >= base["honesty"]
    lines = [
        "",
        "",
        f"**Verdict: {'PASS' if factual_ok and honesty_ok else 'FAIL'}** "
        "(computed from the run files by `scripts/update_eval_matrix.py`)",
        "",
        f"- factual: tuned+RAG {tuned_rag['factual']} vs base+RAG "
        f"{base_rag['factual']} — {'meets' if factual_ok else 'FAILS'} the bar",
        f"- honesty: tuned {tuned['honesty']} vs base {base['honesty']} — "
        f"{'meets' if honesty_ok else 'FAILS'} the bar",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    text = MATRIX.read_text(encoding="utf-8")
    if START not in text or CRITERION not in text:
        print("EVAL_MATRIX.md does not contain the acceptance table", file=sys.stderr)
        return 2

    table, missing = build_table()
    head, rest = text.split(START, 1)
    _, tail = rest.split(CRITERION, 1)
    new = head + table + verdict() + "\n" + CRITERION + tail

    if args.check:
        if new != text:
            print("EVAL_MATRIX.md acceptance table is stale", file=sys.stderr)
            return 1
        print("acceptance table matches the run files")
        return 0

    MATRIX.write_text(new, encoding="utf-8")
    print(f"updated {MATRIX.relative_to(ROOT)}")
    if missing:
        print("still missing: " + ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
