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


class TwoPhaseTests(unittest.TestCase):
    """Judging must not interleave with answering.

    Interleaved, Ollama evicts and reloads weights between the answer model and
    the judge on every probe -- measured at ~2 min/probe on the M4 Air, ~100
    minutes for 50. Batched, it is two model loads. If a future edit moves the
    judge back inside the answer loop the scores stay identical and only the
    wall clock changes, which is exactly the kind of regression nobody notices.
    """

    def test_all_answers_are_produced_before_any_judging(self):
        order = []

        def fake_chat(model, system, user, timeout=180):
            order.append("answer")
            return "some answer"

        def fake_judge(question, reference, candidate, judge_model):
            order.append("judge")
            return 3, None

        probes = [_probe(f"p{i}") for i in range(4)]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/processed/training").mkdir(parents=True)
            (root / evaluate.PROBES_PATH).write_text(
                "".join(json.dumps(p) + "\n" for p in probes), encoding="utf-8"
            )
            with mock.patch.object(evaluate, "run_chat", side_effect=fake_chat), \
                 mock.patch.object(evaluate, "_judge_score", side_effect=fake_judge), \
                 mock.patch.object(evaluate, "_update_baseline_table"):
                summary = evaluate.run_eval(root, "qwen3:8b", use_rag=False)

        self.assertEqual(summary["probes"], 4)
        self.assertEqual(order, ["answer"] * 4 + ["judge"] * 4)

    def test_finished_run_removes_its_resume_crumb(self):
        probes = [_probe("p0")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/processed/training").mkdir(parents=True)
            (root / evaluate.PROBES_PATH).write_text(
                json.dumps(probes[0]) + "\n", encoding="utf-8"
            )
            with mock.patch.object(evaluate, "run_chat", return_value="a"), \
                 mock.patch.object(evaluate, "_judge_score", return_value=(3, None)), \
                 mock.patch.object(evaluate, "_update_baseline_table"):
                evaluate.run_eval(root, "qwen3:8b", use_rag=False)
            self.assertFalse(evaluate._checkpoint_path(root, "qwen3_8b").exists())


class AnswerFailureTests(unittest.TestCase):
    """The answer phase needs the same protection as the judge.

    Hardening only _judge_score on 2026-09-25 left this path bare, and the very
    next run died in it with the identical socket.timeout, 24 probes in.
    """

    def test_answer_timeout_is_retried_then_recorded_not_raised(self):
        calls = []

        def always_timeout(*a, **kw):
            calls.append(1)
            raise OSError("timed out")

        with mock.patch.object(evaluate, "run_chat", side_effect=always_timeout):
            answer, failure = evaluate._answer(
                Path("/nonexistent"), _probe("p1"), "qwen3:8b", use_rag=False
            )

        self.assertEqual(answer, "")
        self.assertIn("timed out", failure)
        self.assertEqual(len(calls), 2, "should retry exactly once")

    def test_answer_gets_a_longer_timeout_than_the_client_default(self):
        seen = {}

        def capture(model, system, user, timeout=180):
            seen["timeout"] = timeout
            return "an answer"

        with mock.patch.object(evaluate, "run_chat", side_effect=capture):
            evaluate._answer(Path("/nonexistent"), _probe("p1"), "qwen3:8b", False)

        self.assertGreater(seen["timeout"], 180)

    def test_one_failed_answer_does_not_stop_the_run(self):
        answers = [OSError("timed out"), OSError("timed out"), "ok", "ok", "ok"]

        def flaky(*a, **kw):
            value = answers.pop(0)
            if isinstance(value, Exception):
                raise value
            return value

        probes = [_probe(f"p{i}", family="transliteration") for i in range(3)]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/processed/training").mkdir(parents=True)
            (root / evaluate.PROBES_PATH).write_text(
                "".join(json.dumps(p) + "\n" for p in probes), encoding="utf-8"
            )
            with mock.patch.object(evaluate, "run_chat", side_effect=flaky), \
                 mock.patch.object(evaluate, "_update_baseline_table"):
                summary = evaluate.run_eval(root, "qwen3:8b", use_rag=False)

        self.assertEqual(summary["probes"], 3)
        self.assertEqual(summary["answer_failures"], 1)


class RagTimeoutTests(unittest.TestCase):
    """The RAG path sends the longest prompts in the suite and must not be the
    one left on the short default timeout.

    It was, until 2026-09-25: ANSWER_TIMEOUT was applied to the bare branch
    only, so 7 of 25 factual probes in the base+RAG run timed out and scored 0,
    reporting 0.415 where the 18 that answered averaged 0.558. An
    infrastructure timeout that silently depresses a baseline also biases the
    acceptance comparison in the tuned model's favour.
    """

    def test_rag_answers_get_the_long_timeout(self):
        seen = {}

        def fake_ask(root, question, model=None, timeout=180, **kw):
            seen["timeout"] = timeout
            return {"answer": "an answer"}

        import abshaar.rag as rag

        with mock.patch.object(rag, "ask", fake_ask):
            evaluate._answer(Path("/nonexistent"), _probe("p1"), "qwen3:8b", use_rag=True)

        self.assertEqual(seen["timeout"], evaluate.ANSWER_TIMEOUT)
        self.assertGreater(seen["timeout"], 180)
