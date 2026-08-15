from __future__ import annotations

import unittest

from abshaar.source_matching import normalize_roman
from abshaar.translit import lint_translit_v1, normalize_translit_v1


class NormalizeTranslitTest(unittest.TestCase):
    def test_doubled_vowels_become_macrons(self) -> None:
        # Single trailing i stays short: the plain style writes long ī as "ee",
        # so mechanical conversion must not guess length beyond the style's rules.
        self.assertEqual(
            normalize_translit_v1("Mainu 'be' di khabar na kaai"),
            "Mainu 'be' di khabar na kāi",
        )
        self.assertEqual(normalize_translit_v1("hoor te sees"), "Hūr te sīs")

    def test_legacy_nasals_unify(self) -> None:
        self.assertEqual(normalize_translit_v1("maiṅ maiṁ maiṉ"), "Main̄ main̄ main̄")
        self.assertEqual(normalize_translit_v1("paṇī"), "Paṇī")  # retroflex ṇ preserved

    def test_ain_and_ghain_symbols(self) -> None:
        self.assertEqual(
            normalize_translit_v1("'Ain te 'ghain da farq na jaanaan"),
            "ʿAin te ġain da farq na jānān",
        )

    def test_quotes_that_are_not_ain_survive(self) -> None:
        self.assertEqual(normalize_translit_v1("mainu 'be' di"), "Mainu 'be' di")

    def test_line_starts_capitalized_but_mixed_case_kept(self) -> None:
        self.assertEqual(normalize_translit_v1("alif Allah\ndil ratta"), "Alif Allah\nDil ratta")

    def test_idempotent(self) -> None:
        once = normalize_translit_v1("aape raanjha hoee ṅ")
        self.assertEqual(normalize_translit_v1(once), once)

    def test_lint_flags_rejected_styles_only(self) -> None:
        self.assertTrue(lint_translit_v1("kaai ṅ"))
        self.assertEqual(lint_translit_v1("kāī n̄ ṇ ʿain ġain"), [])


class StyleInvariantKeyTest(unittest.TestCase):
    def test_macron_and_doubled_styles_share_a_key(self) -> None:
        self.assertEqual(normalize_roman("āpe"), normalize_roman("aape"))
        self.assertEqual(normalize_roman("Hīr"), normalize_roman("Heer"))
        self.assertEqual(normalize_roman("hū"), normalize_roman("hoo"))
        self.assertEqual(normalize_roman("ʿain"), normalize_roman("ain"))
        self.assertEqual(normalize_roman("main̄"), normalize_roman("maiṅ"))

    def test_distinct_words_stay_distinct(self) -> None:
        self.assertNotEqual(normalize_roman("dil"), normalize_roman("dāl"))


if __name__ == "__main__":
    unittest.main()
