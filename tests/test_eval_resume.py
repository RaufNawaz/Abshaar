"""A 50-probe eval is 25-40 minutes of generation on this hardware. Before
2026-09-24 it wrote nothing until the last probe finished, so a single judge
timeout discarded the whole run -- which is exactly what happened.

These pin the two properties that make that survivable: progress is written per
probe and resumed on the next run, and a judge that cannot be reached degrades
one probe instead of killing the run.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from abshaar import evaluate


def _probe(pid: str, family: str = "term") -> dict:
    return {
        "id": pid,
        "category": "factual",
        "task_family": family,
        "question": f"q {pid}",
        "reference": "alpha beta gamma",
    }


class CheckpointTests(unittest.TestCase):
    def test_progress_is_written_after_every_probe(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = [{**_probe("p1"), "answer": "a", "score": 1.0}]
            evaluate._checkpoint(root, "run", results)
            path = evaluate._checkpoint_path(root, "run")
            self.assertTrue(path.exists())
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([r["id"] for r in rows], ["p1"])

    def test_checkpoint_round_trips_and_reports_done_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            evaluate._checkpoint(
                root,
                "run",
                [
                    {**_probe("p1"), "answer": "a", "score": 1.0},
                    {**_probe("p2"), "answer": "b", "score": 0.5},
                ],
            )
            loaded, done = evaluate._load_checkpoint(root, "run")
            self.assertEqual(done, {"p1", "p2"})
            self.assertEqual(len(loaded), 2)

    def test_missing_checkpoint_is_an_empty_start_not_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            loaded, done = evaluate._load_checkpoint(Path(tmp), "never-run")
            self.assertEqual(loaded, [])
            self.assertEqual(done, set())


class JudgeFailureTests(unittest.TestCase):
    def test_judge_timeout_is_retried_then_reported_not_raised(self):
        calls = []

        def always_timeout(*a, **kw):
            calls.append(1)
            raise OSError("timed out")

        with mock.patch.object(evaluate, "run_chat", side_effect=always_timeout):
            score, failure = evaluate._judge_score("q", "ref", "cand", "qwen3:4b")

        self.assertEqual(score, 0)
        self.assertIsNotNone(failure)
        self.assertIn("timed out", failure)
        self.assertEqual(len(calls), 2, "should retry exactly once before giving up")

    def test_judge_recovers_on_the_retry(self):
        replies = [OSError("timed out"), "3"]

        def flaky(*a, **kw):
            value = replies.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        with mock.patch.object(evaluate, "run_chat", side_effect=flaky):
            score, failure = evaluate._judge_score("q", "ref", "cand", "qwen3:4b")

        self.assertEqual(score, 3)
        self.assertIsNone(failure)

    def test_judge_gets_a_longer_timeout_than_the_default(self):
        seen = {}

        def capture(model, system, user, timeout=180):
            seen["timeout"] = timeout
            return "2"

        with mock.patch.object(evaluate, "run_chat", side_effect=capture):
            evaluate._judge_score("q", "ref", "cand", "qwen3:4b")

        # the judge is a different model, so Ollama reloads weights per probe
        self.assertGreater(seen["timeout"], 180)


if __name__ == "__main__":
    unittest.main()
