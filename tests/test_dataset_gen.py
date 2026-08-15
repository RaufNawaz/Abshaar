from __future__ import annotations

import unittest

from abshaar.dataset_gen import split_examples, strip_attribution_notes


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
