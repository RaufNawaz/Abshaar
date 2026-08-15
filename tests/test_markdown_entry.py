from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from abshaar.markdown_entry import entry_to_poem_record, parse_markdown_entry
ENTRY = """---
id: bulleh_shah_9999
poet_id: bulleh_shah
title: "Test poem"
work_type: "kafi"
source_ids:
  - source_test
rights_status: "project-original"
review_status: "publishable"
---

# Original

اصل لائن
دوجی لائن

# Script Notes

- Script: Shahmukhi
- Language spans: Punjabi

# Transliteration

asal line
dooji line

# Literal Gloss

literal gloss

# AI Translation

ai translation

# Literary Translation

literary translation

# Tashreeh

explanation

# Key Terms

- ishq:

# Themes

- divine_love

# Source Notes

- Can this be published? yes
"""


RAFAT_LITERAL_SECTION = """# Literal Translation

A rendered English verse line,
and another rendered line.

_Reference translation by Taufiq Rafat, "Bulleh Shah: A Selection" (Vanguard, 1982), p.35. COPYRIGHTED — private reference only; do NOT publish or use for training._
"""

AI_DRAFTED_SECTIONS = """# Literary Translation

An original literary rendering.

_AI-drafted (Claude) literary rendering from the Urdu original. Draft for your review; replace with your own._

# Tashreeh

An analytical explanation.

_AI-drafted (Claude) analytical tashreeh; needs review._
"""


def _record_from(entry_text: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bulleh_shah_9999.md"
        path.write_text(entry_text, encoding="utf-8")
        return entry_to_poem_record(parse_markdown_entry(path))


class MarkdownEntryTest(unittest.TestCase):
    def test_entry_to_poem_record(self) -> None:
        record = _record_from(ENTRY)

        self.assertEqual(record["id"], "bulleh_shah_9999")
        self.assertEqual(record["original"]["script"], "Shahmukhi")
        self.assertEqual(len(record["segmentation"]), 2)
        self.assertIn("term_ishq_bulleh_shah", record["glossary_terms"])
        self.assertIn("theme_divine_love", record["themes"])
        self.assertEqual(
            [translation["kind"] for translation in record["translations"]],
            ["literal_gloss", "ai_translation", "literary_translation"],
        )
        self.assertEqual(record["translations"][1]["text"], "ai translation")
        self.assertEqual(record["translations"][1]["model"], "claude")
        self.assertTrue(record["publication"]["include_on_website"])

    def test_plain_literal_gloss_stays_literal_and_trainable(self) -> None:
        record = _record_from(ENTRY)
        literal = record["translations"][0]
        self.assertEqual(literal["kind"], "literal_gloss")
        self.assertEqual(literal["created_by"], "human")
        self.assertEqual(literal["rights"], "project")
        self.assertTrue(literal["trainable"])

    def test_rafat_reference_becomes_reference_translation(self) -> None:
        record = _record_from(ENTRY.replace("# Literal Gloss\n\nliteral gloss\n", RAFAT_LITERAL_SECTION))
        reference = record["translations"][0]
        self.assertEqual(reference["kind"], "reference_translation")
        self.assertEqual(reference["id"], "trans_bulleh_shah_9999_reference")
        self.assertEqual(reference["rights"], "copyrighted")
        self.assertIs(reference["trainable"], False)
        self.assertIs(reference["publishable"], False)

    def test_ai_drafted_markers_set_attribution(self) -> None:
        record = _record_from(
            ENTRY.replace(
                "# Literary Translation\n\nliterary translation\n\n# Tashreeh\n\nexplanation\n",
                AI_DRAFTED_SECTIONS,
            )
        )
        literary = record["translations"][2]
        self.assertEqual(literary["created_by"], "ai")
        self.assertEqual(literary["model"], "claude")
        tashreeh = record["tashreeh"][0]
        self.assertEqual(tashreeh["created_by"], "ai")
        self.assertEqual(tashreeh["model"], "claude")


if __name__ == "__main__":
    unittest.main()
