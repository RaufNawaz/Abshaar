from __future__ import annotations

import unittest

from abshaar.text import has_placeholder


TEMPLATE_PLACEHOLDERS = [
    "[first line or working title]",
    "[Paste or type original source-script text here.]",
    "[Type Latin transliteration here, line by line.]",
    "[Reference translation, e.g. a published translator's rendering, with citation.]",
    "[AI-drafted English translation, for human review.]",
    "[Your own literary translation.]",
    "[Explanation of metaphor, cultural context, metaphysical meaning, ambiguity, and alternate readings.]",
    "[Human-reviewed answer grounded in glossary and poems.]",
    "[Explain how Bulleh Shah uses this term in the selected corpus.]",
    "[Add uncertainty and alternate readings.]",
    "[literal gloss here]",
    "[clearly labeled AI translation draft here]",
    "[project literary translation here]",
    "[model name]",
    "[prompt version]",
    "[TODO: verify this reading]",
    "Can this be published? yes/no/unknown",
    "Rights status: public-domain/permission-cleared",
]

CORPUS_CONVENTIONS = [
    "[uncertain line — torn apart in the middle, left hanging upside down].",
    "[torn line — left hanging; reading uncertain].",
    "[wild beasts lie in wait,] they block the paths;",
    "See [[bulleh_shah_0001]] for the Sufinama witness of this kafi.",
    "They [all] say the same thing.",
    "[my master] alone knows.",
    "[and swear]",
    "[Uncertain line]",
    "[~ set upon the pyre/fire]",
    "[Zakariya's head was laid to the saw]",
]


class HasPlaceholderTest(unittest.TestCase):
    def test_template_placeholders_are_flagged(self) -> None:
        for text in TEMPLATE_PLACEHOLDERS:
            with self.subTest(text=text):
                self.assertTrue(has_placeholder(text))

    def test_corpus_bracket_conventions_are_not_flagged(self) -> None:
        for text in CORPUS_CONVENTIONS:
            with self.subTest(text=text):
                self.assertFalse(has_placeholder(text))

    def test_recurses_into_lists_and_dicts(self) -> None:
        self.assertTrue(has_placeholder({"a": ["clean", "[Your own literary translation.]"]}))
        self.assertFalse(has_placeholder({"a": ["clean", ["[uncertain line]"]], "b": None}))


if __name__ == "__main__":
    unittest.main()
