from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from abshaar.jsonl import write_jsonl
from abshaar.source_matching import match_source_manifest


ENTRY = """---
id: bulleh_shah_0001
poet_id: bulleh_shah
title: "Ranjha Ranjha kardi ni main aape Ranjha hoi"
work_type: "kafi"
source_ids:
  - source_test
rights_status: "public-domain"
review_status: "draft"
---

# Original

رانجھا رانجھا کر دی نی میں آپے رانجھا ہوئی

# Transliteration

Ranjha Ranjha kardi ni main aape Ranjha hoi
"""


class SourceMatchingTest(unittest.TestCase):
    def test_matches_roman_and_urdu_first_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            working = root / "data" / "working"
            working.mkdir(parents=True)
            (working / "bulleh_shah_0001.md").write_text(ENTRY, encoding="utf-8")

            manifest = root / "manifest.jsonl"
            write_jsonl(
                manifest,
                [
                    {
                        "id": "sufinama_bulleh_kaafi_12",
                        "source_id": "source_sufinama_bulleh_catalog",
                        "url": "https://sufinama.org/kaafi/bulleh-shah-kaafi-12",
                        "url_urdu": "https://sufinama.org/kaafi/bulleh-shah-kaafi-12?lang=ur",
                        "roman_title": "ranjha ranjha kardi ni main aape ranjha hoi",
                        "urdu_title": "رانجھا رانجھا کر دی نی میں آپے رانجھا ہوئی",
                    }
                ],
            )
            output = root / "matches.jsonl"
            matches = match_source_manifest(root, manifest, output, top_n=1)

        self.assertEqual(matches[0]["candidate_poems"][0]["poem_id"], "bulleh_shah_0001")
        self.assertEqual(matches[0]["candidate_poems"][0]["score"], 1.0)
        self.assertEqual(matches[0]["match_status"], "needs_review")

    def test_accepts_catalog_field_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            working = root / "data" / "working"
            working.mkdir(parents=True)
            (working / "bulleh_shah_0001.md").write_text(ENTRY, encoding="utf-8")
            manifest = root / "catalog.jsonl"
            write_jsonl(
                manifest,
                [
                    {
                        "id": "catalog_item",
                        "source_id": "source_catalog",
                        "url_roman": "https://sufinama.org/kaafi/example",
                        "url_urdu": "https://sufinama.org/kaafi/example?lang=ur",
                        "title_roman": "ranjha ranjha kardi ni main aape ranjha hoi",
                        "title_urdu": "رانجھا رانجھا کر دی نی میں آپے رانجھا ہوئی",
                    }
                ],
            )
            matches = match_source_manifest(root, manifest, root / "matches.jsonl", top_n=1)

        self.assertEqual(matches[0]["source_url"], "https://sufinama.org/kaafi/example")
        self.assertEqual(matches[0]["candidate_poems"][0]["poem_id"], "bulleh_shah_0001")


if __name__ == "__main__":
    unittest.main()
