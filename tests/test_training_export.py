from __future__ import annotations

import unittest

from abshaar.training_export import extract_trainable_layers


REFERENCE_TEXT = (
    "A for Allah who has my heart, I have no knowledge of B, "
    "nor do I know what it means, while A savours sweet to me."
)


def _record(literal_kind: str, ai_text: str) -> dict:
    return {
        "id": "bulleh_shah_9999",
        "source_ids": ["source_test"],
        "original": {"text": "اصل لائن"},
        "transliteration": {"text": "asal line"},
        "translations": [
            {
                "id": "trans_bulleh_shah_9999_reference",
                "kind": literal_kind,
                "text": REFERENCE_TEXT,
                "rights": "copyrighted",
                "publishable": False,
                "trainable": False,
                "created_by": "human",
                "model": None,
            },
            {
                "id": "trans_bulleh_shah_9999_ai",
                "kind": "ai_translation",
                "text": ai_text,
                "rights": "project",
                "trainable": True,
                "created_by": "ai",
                "model": "claude",
            },
        ],
        "tashreeh": [
            {
                "id": "tash_bulleh_shah_9999_beginner",
                "text": "An explanation with an [uncertain line] marker.",
                "rights": "project",
                "trainable": True,
                "created_by": "ai",
                "model": "claude",
            }
        ],
    }


class TrainingExportTest(unittest.TestCase):
    def test_reference_translation_is_never_emitted(self) -> None:
        layers, leaks = extract_trainable_layers(
            [_record("reference_translation", "An independent original rendering.")]
        )
        self.assertEqual(leaks, [])
        kinds = {layer["kind"] for layer in layers}
        self.assertNotIn("reference_translation", kinds)
        self.assertEqual(
            kinds, {"original", "transliteration", "ai_translation", "tashreeh"}
        )
        self.assertTrue(all(layer["trainable"] for layer in layers))

    def test_leak_is_fatal(self) -> None:
        leaked = "My draft: a for allah who has my heart i have no knowledge of b at all."
        layers, leaks = extract_trainable_layers([_record("reference_translation", leaked)])
        self.assertTrue(leaks, "an 8-gram overlap with the reference must be reported")
        self.assertIn("trans_bulleh_shah_9999_ai", leaks[0])

    def test_uncertainty_flag_from_markers(self) -> None:
        layers, _ = extract_trainable_layers(
            [_record("reference_translation", "Clean independent rendering.")]
        )
        by_kind = {layer["kind"]: layer for layer in layers}
        self.assertTrue(by_kind["tashreeh"]["uncertainty"])
        self.assertFalse(by_kind["ai_translation"]["uncertainty"])

    def test_short_reference_uses_containment(self) -> None:
        record = _record("reference_translation", "ok text")
        record["translations"][0]["text"] = "Short copyrighted line"
        record["translations"][1]["text"] = "Here is the short copyrighted line, copied."
        _, leaks = extract_trainable_layers([record])
        self.assertTrue(leaks)


if __name__ == "__main__":
    unittest.main()
