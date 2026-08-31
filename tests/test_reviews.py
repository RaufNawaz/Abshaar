from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from abshaar.dataset_gen import GenerationPolicy, build_examples
from abshaar.reviews import apply_to_layers, load_corrections


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class LoadCorrectionsTest(unittest.TestCase):
    def _root(self, reviews: list[dict]) -> Path:
        root = Path(tempfile.mkdtemp())
        _write(root / "data" / "annotations" / "reviews.jsonl", reviews)
        return root

    def test_template_placeholders_are_not_corrections(self) -> None:
        root = self._root([{
            "id": "r1", "poem_id": "bulleh_shah_0001", "reviewer": "[name]",
            "corrected_translation": "[corrected translation]",
        }])
        self.assertEqual(load_corrections(root), {})

    def test_bracketed_uncertainty_inside_a_correction_is_kept(self) -> None:
        text = "The first line.\n[uncertain line — torn in the scan]\nThe third line."
        root = self._root([{
            "id": "r1", "poem_id": "bulleh_shah_0001", "reviewer": "Rauf",
            "corrected_translation": text,
        }])
        corrections = load_corrections(root)
        self.assertEqual(corrections["bulleh_shah_0001"]["literary_translation"]["text"], text)

    def test_unnamed_reviewer_is_ignored(self) -> None:
        root = self._root([{
            "id": "r1", "poem_id": "bulleh_shah_0001", "reviewer": "",
            "corrected_tashreeh": "A real correction.",
        }])
        self.assertEqual(load_corrections(root), {})

    def test_later_review_supersedes_earlier(self) -> None:
        root = self._root([
            {"id": "r1", "poem_id": "p1", "reviewer": "Rauf", "corrected_tashreeh": "first"},
            {"id": "r2", "poem_id": "p1", "reviewer": "Rauf", "corrected_tashreeh": "second"},
        ])
        self.assertEqual(load_corrections(root)["p1"]["tashreeh"]["text"], "second")


class ApplyToLayersTest(unittest.TestCase):
    def test_correction_replaces_rather_than_appends(self) -> None:
        layers = [{"id": "p1:tashreeh", "poem_id": "p1", "kind": "tashreeh",
                   "text": "ai version", "created_by": "ai", "model": "claude"}]
        corrections = {"p1": {"tashreeh": {"text": "human version", "reviewer": "Rauf",
                                           "review_id": "r1", "date": "2026-08-31"}}}
        result = apply_to_layers(layers, corrections)
        self.assertEqual(len(result), 1, "a correction must replace the AI layer, not sit beside it")
        self.assertEqual(result[0]["text"], "human version")
        self.assertEqual(result[0]["created_by"], "human")
        self.assertEqual(result[0]["supersedes"], "p1:tashreeh")
        self.assertNotIn("ai version", json.dumps(result))

    def test_correction_for_a_missing_layer_is_still_added(self) -> None:
        corrections = {"p1": {"tashreeh": {"text": "human only", "reviewer": "Rauf",
                                           "review_id": "r1", "date": "2026-08-31"}}}
        result = apply_to_layers([], corrections)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["created_by"], "human")


class GeneratorPrecedenceTest(unittest.TestCase):
    """The invariant: a reviewed poem never trains the model on the AI draft."""

    def _root(self, reviews: list[dict]) -> Path:
        root = Path(tempfile.mkdtemp())
        poem = {
            "id": "bulleh_shah_0001",
            "title": "Test Kafi",
            "original": {"text": "سطر اول\nسطر دوم"},
            "transliteration": {"text": "satr-e awwal\nsatr-e dom"},
            "translations": [
                {"id": "t1", "kind": "literary_translation", "text": "AI DRAFT TRANSLATION",
                 "trainable": True, "created_by": "ai"},
                {"id": "t2", "kind": "ai_translation", "text": "OTHER AI TRANSLATION",
                 "trainable": True, "created_by": "ai"},
            ],
            "tashreeh": [{"id": "s1", "text": "AI DRAFT TASHREEH", "trainable": True, "created_by": "ai"}],
            "source_ids": [],
        }
        _write(root / "data" / "processed" / "poems.jsonl", [poem])
        _write(root / "data" / "processed" / "private" / "knowledge_base.jsonl", [])
        _write(root / "data" / "annotations" / "reviews.jsonl", reviews)
        return root

    def test_ai_draft_is_absent_once_the_poem_is_reviewed(self) -> None:
        root = self._root([{
            "id": "r1", "poem_id": "bulleh_shah_0001", "reviewer": "Rauf",
            "corrected_translation": "HUMAN TRANSLATION",
            "corrected_tashreeh": "HUMAN TASHREEH",
        }])
        blob = json.dumps(build_examples(root, GenerationPolicy()), ensure_ascii=False)
        self.assertIn("HUMAN TRANSLATION", blob)
        self.assertIn("HUMAN TASHREEH", blob)
        self.assertNotIn("AI DRAFT TRANSLATION", blob)
        self.assertNotIn("AI DRAFT TASHREEH", blob)
        self.assertNotIn("OTHER AI TRANSLATION", blob)

    def test_unreviewed_poem_still_uses_the_ai_draft(self) -> None:
        blob = json.dumps(build_examples(self._root([]), GenerationPolicy()), ensure_ascii=False)
        self.assertIn("AI DRAFT TRANSLATION", blob)

    def test_examples_record_whether_they_are_human_reviewed(self) -> None:
        root = self._root([{
            "id": "r1", "poem_id": "bulleh_shah_0001", "reviewer": "Rauf",
            "corrected_translation": "HUMAN TRANSLATION",
        }])
        examples = build_examples(root, GenerationPolicy())
        translation = [e for e in examples if e["task_family"] == "translation"]
        self.assertTrue(translation, "expected a translation example")
        self.assertTrue(all(e["human_reviewed"] for e in translation))
