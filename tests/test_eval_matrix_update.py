"""The acceptance verdict decides whether run 2 ships, so it must be computed
from the run files and must refuse to guess.

The failure this guards against is a table that reads PASS because three runs
finished and the fourth was assumed, or because someone transcribed a number
from a log into a document and it drifted.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "update_eval_matrix", ROOT / "scripts" / "update_eval_matrix.py"
)
uem = importlib.util.module_from_spec(_spec)
sys.modules["update_eval_matrix"] = uem
_spec.loader.exec_module(uem)


def _summary(factual, honesty, judge_failures=0):
    return {
        "summary": {
            "factual": factual,
            "honesty": honesty,
            "disputed": 0.0,
            "probes": 50,
            "judge": "qwen3:4b",
            "judge_failures": judge_failures,
        }
    }


class VerdictTests(unittest.TestCase):
    def _with_runs(self, runs):
        def fake_load(stem):
            return runs[stem]["summary"] if stem in runs else None

        return mock.patch.object(uem, "load", side_effect=fake_load)

    def test_no_verdict_when_any_run_is_missing(self):
        runs = {
            "qwen3_8b": _summary(0.5, 0.8),
            "qwen3_8b_rag": _summary(0.6, 0.9),
            "mlx_run2": _summary(0.55, 0.85),
            # mlx_run2_rag deliberately absent
        }
        with self._with_runs(runs):
            self.assertIn("cannot be computed", uem.verdict())

    def test_pass_requires_both_criteria(self):
        runs = {
            "qwen3_8b": _summary(0.50, 0.80),
            "qwen3_8b_rag": _summary(0.60, 0.90),
            "mlx_run2": _summary(0.55, 0.85),
            "mlx_run2_rag": _summary(0.65, 0.95),
        }
        with self._with_runs(runs):
            self.assertIn("PASS", uem.verdict())

    def test_better_factual_does_not_excuse_worse_honesty(self):
        """A model that hallucinates more than base is rejected regardless of
        style gains -- the criterion says so verbatim."""
        runs = {
            "qwen3_8b": _summary(0.50, 0.90),
            "qwen3_8b_rag": _summary(0.60, 0.90),
            "mlx_run2": _summary(0.55, 0.40),   # much worse honesty
            "mlx_run2_rag": _summary(0.99, 0.95),  # much better factual
        }
        with self._with_runs(runs):
            result = uem.verdict()
        self.assertIn("FAIL", result)
        self.assertIn("honesty", result)

    def test_judge_failures_are_surfaced_in_the_row(self):
        runs = {"qwen3_8b": _summary(0.5, 0.8, judge_failures=7)}
        with self._with_runs(runs):
            table, missing = uem.build_table()
        self.assertIn("7 judge failures", table)
        self.assertIn("qwen3_8b_rag", missing)


if __name__ == "__main__":
    unittest.main()
