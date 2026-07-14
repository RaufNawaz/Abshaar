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


class MarkdownEntryTest(unittest.TestCase):
    def test_entry_to_poem_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bulleh_shah_9999.md"
            path.write_text(ENTRY, encoding="utf-8")
            entry = parse_markdown_entry(path)
            record = entry_to_poem_record(entry)

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


if __name__ == "__main__":
    unittest.main()
