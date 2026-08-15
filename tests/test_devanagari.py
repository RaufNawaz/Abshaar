from __future__ import annotations

import unittest

from abshaar.devanagari import transliterate_devanagari
from abshaar.source_matching import (
    DEVANAGARI_SCORE_CAP,
    _score_item,
    normalize_roman,
)


class TransliterationTest(unittest.TestCase):
    def test_common_punjabi_words(self) -> None:
        cases = {
            "रांझा": "ranjha",
            "बुल्ला": "bulla",
            "करदी": "karadi",
            "इश्क़": "ishqa",
            "अलिफ़": "alifa",
            "दिल": "dila",
        }
        for devanagari, expected in cases.items():
            with self.subTest(devanagari=devanagari):
                self.assertEqual(transliterate_devanagari(devanagari), expected)

    def test_virama_kills_inherent_vowel(self) -> None:
        self.assertEqual(transliterate_devanagari("बुल्ल्हे"), "bullhe")

    def test_danda_becomes_space_and_digits_map(self) -> None:
        self.assertEqual(transliterate_devanagari("१।२"), "1 2")

    def test_fuzzy_proximity_to_roman(self) -> None:
        from difflib import SequenceMatcher

        result = normalize_roman(transliterate_devanagari("रांझा रांझा करदी नी"))
        target = normalize_roman("ranjha ranjha kardi ni")
        self.assertGreater(SequenceMatcher(None, result, target).ratio(), 0.85)


class DevanagariMatchingTest(unittest.TestCase):
    CANDIDATE = {
        "poem_id": "bulleh_shah_0001",
        "title": "Ranjha Ranjha kardi ni main",
        "roman_lines": ["Ranjha Ranjha kardi ni main aape Ranjha hoi"],
        "urdu_lines": ["رانجھا رانجھا کردی نی میں آپے رانجھا ہوئی"],
    }

    def test_devanagari_only_item_gets_a_candidate(self) -> None:
        item = {
            "id": "test_item",
            "devanagari_title": "रांझा रांझा करदी नी मैं",
            "devanagari_text": "रांझा रांझा करदी नी मैं आपे रांझा होई",
        }
        result = _score_item(item, self.CANDIDATE)
        self.assertGreater(result["score"], 0.75)
        self.assertIn("devanagari_any_line", result["signals"])

    def test_devanagari_score_never_reaches_auto_merge(self) -> None:
        item = {
            "id": "test_item",
            "devanagari_text": "रांझा रांझा करदी नी मैं आपे रांझा होई",
        }
        result = _score_item(item, self.CANDIDATE)
        self.assertLessEqual(result["score"], DEVANAGARI_SCORE_CAP)
        self.assertLess(result["score"], 1.0)

    def test_roman_exact_still_reaches_one(self) -> None:
        item = {
            "id": "test_item",
            "roman_text": "Ranjha Ranjha kardi ni main aape Ranjha hoi",
        }
        result = _score_item(item, self.CANDIDATE)
        self.assertEqual(result["score"], 1.0)


if __name__ == "__main__":
    unittest.main()
