from __future__ import annotations

import json
import unittest
from pathlib import Path

from abshaar.dataset_gen import (
    GenerationPolicy,
    build_examples,
    run_gates,
    split_examples,
    strip_attribution_notes,
)


def _example(id_: str, work: str) -> dict:
    return {
        "id": id_,
        "task_family": "translation",
        "messages": [
            {"role": "system", "content": "s"},
            {"role": "user", "content": f"q {id_}"},
            {"role": "assistant", "content": "a"},
        ],
        "kb_ids": [],
        "poem_ids": [],
        "canonical_work_id": work,
        "generator": "template_v1",
        "uncertainty": False,
    }


class StripAttributionTest(unittest.TestCase):
    def test_trailing_notes_removed(self) -> None:
        text = (
            "Line one of the translation.\nLine two.\n\n"
            "_AI-drafted (Claude) from the Urdu original; needs review._"
        )
        self.assertEqual(strip_attribution_notes(text), "Line one of the translation.\nLine two.")

    def test_stacked_notes_removed(self) -> None:
        text = "Body.\n\n_Note one._\n_Note two._"
        self.assertEqual(strip_attribution_notes(text), "Body.")

    def test_mid_text_emphasis_kept(self) -> None:
        text = "The word _fana_ appears mid-line.\nMore text."
        self.assertEqual(strip_attribution_notes(text), text)


class SplitTest(unittest.TestCase):
    def test_clusters_never_straddle_splits(self) -> None:
        examples = [_example(f"e{i}", f"work_{i % 20:03d}") for i in range(200)]
        train, eval_set, eval_works = split_examples(examples)
        train_works = {e["canonical_work_id"] for e in train}
        eval_split_works = {e["canonical_work_id"] for e in eval_set}
        self.assertEqual(train_works & eval_split_works, set())
        self.assertEqual(len(train) + len(eval_set), 200)
        self.assertTrue(eval_works)

    def test_split_is_marked_on_examples(self) -> None:
        examples = [_example(f"e{i}", f"work_{i:03d}") for i in range(20)]
        train, eval_set, _ = split_examples(examples)
        self.assertTrue(all(e["split"] == "train" for e in train))
        self.assertTrue(all(e["split"] == "eval" for e in eval_set))


if __name__ == "__main__":
    unittest.main()


class GenerationPolicyTest(unittest.TestCase):
    """The policy flags open specific gates; the gates must still hold by default."""

    def test_default_policy_is_conservative(self) -> None:
        policy = GenerationPolicy()
        self.assertFalse(policy.include_reference_translations)
        self.assertFalse(policy.include_witnesses)
        self.assertTrue(policy.holdout)

    def test_unrestricted_opens_every_gate_but_keeps_the_holdout(self) -> None:
        policy = GenerationPolicy.unrestricted()
        self.assertTrue(policy.include_reference_translations)
        self.assertTrue(policy.include_witnesses)
        self.assertTrue(policy.holdout, "the holdout is not part of 'unrestricted'; losing it destroys measurement")

    def test_leak_gate_still_fires_when_reference_text_is_not_invited(self) -> None:
        """Regression guard: adding the opt-in must not have disabled the gate."""
        reference = "the cotton bolls are white and the spinning wheel turns slowly at dawn today"
        leaked = _example("ex_leak", "work_a")
        leaked["messages"][2]["content"] = reference
        failures = run_gates([leaked], [leaked], [], [reference], GenerationPolicy())
        self.assertTrue(any("8-gram" in f for f in failures), failures)

    def test_leak_gate_is_skipped_only_when_reference_text_is_invited(self) -> None:
        reference = "the cotton bolls are white and the spinning wheel turns slowly at dawn today"
        leaked = _example("ex_leak", "work_a")
        leaked["messages"][2]["content"] = reference
        failures = run_gates(
            [leaked], [leaked], [], [reference],
            GenerationPolicy(include_reference_translations=True),
        )
        self.assertEqual([f for f in failures if "8-gram" in f], [])

    def test_disabling_the_holdout_puts_everything_in_train(self) -> None:
        examples = [_example(f"ex_{i}", f"work_{i}") for i in range(30)]
        train, eval_set, eval_works = split_examples(examples, holdout=False)
        self.assertEqual(len(train), 30)
        self.assertEqual(eval_set, [])
        self.assertEqual(eval_works, [])
        self.assertTrue(all(e["split"] == "train" for e in train))

    def test_holdout_still_splits_by_cluster(self) -> None:
        examples = [_example(f"ex_{i}", f"work_{i}") for i in range(30)]
        train, eval_set, _ = split_examples(examples, holdout=True)
        self.assertTrue(eval_set, "a holdout build must actually hold something out")
        train_works = {e["canonical_work_id"] for e in train}
        eval_works = {e["canonical_work_id"] for e in eval_set}
        self.assertEqual(train_works & eval_works, set())


class CitationResolutionTest(unittest.TestCase):
    """Every kb_id the generator emits must exist in the knowledge base.

    Added after 63 tashreeh examples were found citing `tash_<poem>_beginner`
    while the record is `kb:tash_<poem>_beginner`. Nothing reached the model —
    the mlx export carries only `messages` — but provenance that does not
    resolve is provenance you cannot audit.

    This exercises the generator, not a committed artifact: a dataset file on
    disk may predate the fix, and that is a stale export, not a live defect.
    """

    def test_generated_citations_resolve_against_the_knowledge_base(self) -> None:
        root = Path(__file__).resolve().parents[1]
        kb_path = root / "data" / "processed" / "private" / "knowledge_base.jsonl"
        if not kb_path.exists():
            self.skipTest("knowledge base not built in this checkout")

        kb_ids = {json.loads(line)["id"] for line in kb_path.open(encoding="utf-8") if line.strip()}
        unresolved: dict[str, int] = {}
        for example in build_examples(root, GenerationPolicy.unrestricted()):
            for kb_id in example.get("kb_ids") or []:
                if kb_id not in kb_ids:
                    unresolved[example["task_family"]] = unresolved.get(example["task_family"], 0) + 1
        self.assertEqual(unresolved, {}, f"unresolvable kb_ids by family: {unresolved}")
