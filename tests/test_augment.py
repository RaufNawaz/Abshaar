from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from abshaar.augment import augment_training_data


def _example(id_: str, family: str, question: str, answer: str = "corpus answer") -> dict:
    return {
        "id": id_,
        "task_family": family,
        "messages": [
            {"role": "system", "content": "s"},
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ],
        "kb_ids": [],
        "poem_ids": [],
        "canonical_work_id": "",
        "generator": "template_v1",
        "uncertainty": False,
        "split": "train",
    }


def _make_root(tmp: str) -> Path:
    root = Path(tmp)
    train = [
        _example("ex_term_00001", "term", "What does ishq mean in Bulleh Shah's poetry?"),
        _example("ex_translation_00002", "translation", "Translate this original:\n\nاصل لائن"),
    ]
    eval_set = [_example("ex_term_09999", "term", "Explain the term fana.")]
    for name, records in [("train.jsonl", train), ("eval.jsonl", eval_set)]:
        path = root / "data/processed/training" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    (root / "data/processed/poems.jsonl").write_text("", encoding="utf-8")
    return root


class AugmentTest(unittest.TestCase):
    def test_verified_paraphrase_is_appended_with_verbatim_answer(self) -> None:
        def chat(model: str, system: str, user: str) -> str:
            if "Rewrite" in user:
                return "How is ishq to be understood in Bulleh Shah's verse?"
            return "YES"

        with tempfile.TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            stats, failures = augment_training_data(root, chat, "gen", "ver", per_family_limit=5)
            train = [
                json.loads(line)
                for line in (root / "data/processed/training/train.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]

        self.assertEqual(failures, [])
        self.assertEqual(stats["kept"], 1)
        augmented = [e for e in train if e["id"].startswith("ex_aug_")]
        self.assertEqual(len(augmented), 1)
        self.assertEqual(augmented[0]["messages"][2]["content"], "corpus answer")
        self.assertIn("paraphrase:gen|verify:ver", augmented[0]["generator"])
        # translation family embeds source script and must not be augmented
        self.assertFalse(any(e["task_family"] == "translation" for e in augmented))

    def test_verifier_no_drops_paraphrase(self) -> None:
        def chat(model: str, system: str, user: str) -> str:
            if "Rewrite" in user:
                return "A completely different question about geography?"
            return "NO"

        with tempfile.TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            stats, failures = augment_training_data(root, chat, "gen", "ver")

        self.assertEqual(failures, [])
        self.assertEqual(stats["kept"], 0)
        self.assertEqual(stats["rejected"], 1)

    def test_duplicate_paraphrase_fails_gates(self) -> None:
        def chat(model: str, system: str, user: str) -> str:
            if "Rewrite" in user:
                return "Explain the term fana."  # collides with an eval question
            return "YES"

        with tempfile.TemporaryDirectory() as tmp:
            root = _make_root(tmp)
            stats, failures = augment_training_data(root, chat, "gen", "ver")

        self.assertTrue(failures)
        self.assertEqual(stats, {})


if __name__ == "__main__":
    unittest.main()
