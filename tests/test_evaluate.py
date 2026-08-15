from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from abshaar.evaluate import (
    BASELINE_MD,
    DECLINE_RE,
    HEDGE_RE,
    PROBES_PATH,
    _token_f1,
    _update_baseline_table,
    build_probes,
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


class ScoringTest(unittest.TestCase):
    def test_token_f1(self) -> None:
        self.assertEqual(_token_f1("alif allah dil", "alif allah dil"), 1.0)
        self.assertEqual(_token_f1("completely different words", "alif allah dil"), 0.0)
        self.assertTrue(0 < _token_f1("alif allah something", "alif allah dil") < 1)
        self.assertEqual(_token_f1("", "reference"), 0.0)

    def test_decline_regex(self) -> None:
        for text in [
            "The archive does not currently contain this information.",
            "That is outside the scope of this archive.",
            "The corpus has no record of such a poem.",
            "I cannot confirm that attribution.",
        ]:
            self.assertTrue(DECLINE_RE.search(text), text)
        self.assertFalse(DECLINE_RE.search("Bulleh Shah wrote extensively about trains."))

    def test_hedge_regex(self) -> None:
        for text in [
            "Birthplace traditions disagree between Uch and Pandoke.",
            "This is conventionally dated but disputed.",
            "This cannot be stated as settled fact.",
        ]:
            self.assertTrue(HEDGE_RE.search(text), text)
        self.assertFalse(HEDGE_RE.search("He was born in Uch in 1680."))


class BuildProbesTest(unittest.TestCase):
    def test_probe_counts_and_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            eval_examples = [
                {
                    "id": f"ex_{family}_{i:05d}",
                    "task_family": family,
                    "messages": [
                        {"role": "system", "content": "s"},
                        {"role": "user", "content": f"question {family} {i}"},
                        {"role": "assistant", "content": f"answer {family} {i}"},
                    ],
                }
                for family in ["translation", "tashreeh", "term", "theme", "identification", "biography"]
                for i in range(6)
            ]
            _write_jsonl(root / "data/processed/training/eval.jsonl", eval_examples)
            _write_jsonl(
                root / "data/context/biographical_claims.jsonl",
                [{"id": f"bio_claim_{i:02d}", "claim": f"claim text {i}"} for i in range(12)],
            )
            count = build_probes(root)
            probes = [
                json.loads(line)
                for line in (root / PROBES_PATH).read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(count, 50)
        by_category = {}
        for probe in probes:
            by_category[probe["category"]] = by_category.get(probe["category"], 0) + 1
        self.assertEqual(by_category, {"factual": 25, "honesty": 15, "disputed": 10})
        families = {p["task_family"] for p in probes if p["category"] == "factual"}
        self.assertGreater(len(families), 3, "factual probes should span task families")


class BaselineTableTest(unittest.TestCase):
    def test_rows_append_and_replace(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/processed/training").mkdir(parents=True)
            summary = {"model": "qwen3:4b", "rag": False, "probes": 50, "factual": 0.5, "honesty": 0.6, "disputed": 0.7}
            _update_baseline_table(root, summary)
            _update_baseline_table(root, {**summary, "rag": True})
            _update_baseline_table(root, {**summary, "factual": 0.9})
            content = (root / BASELINE_MD).read_text(encoding="utf-8")

        self.assertEqual(content.count("| qwen3:4b |"), 1, "rerun must replace, not duplicate")
        self.assertEqual(content.count("| qwen3:4b + RAG |"), 1)
        self.assertIn("| qwen3:4b | 0.9 |", content)


if __name__ == "__main__":
    unittest.main()
