from __future__ import annotations

import unittest

from abshaar.gurmukhi_pdf import _audit, segment_page_texts


class GurmukhiPdfTest(unittest.TestCase):
    def test_segments_multiple_headings_and_page_spans(self) -> None:
        pages = [
            "cover only",
            (
                "www.PunjabLibrary.com\n1. ਪਹਿਲੀ ਕਾਫ਼ੀ\nਪਹਿਲੀ ਪੰਕਤੀ\n"
                "2. ਦੂਜੀ ਕਾਫ਼ੀ\nਦੂਜੀ ਪੰਕਤੀ"
            ),
            (
                "ਦੂਜੀ ਜਾਰੀ\n3. ਤੀਜੀ ਕਾਫ਼ੀ\nਤੀਜੀ ਪੰਕਤੀ\n"
                "www.PunjabLibrary.com"
            ),
            "www.PunjabLibrary.com\n4. ਚੌਥੀ ਕਾਫ਼ੀ\nਚੌਥੀ ਪੰਕਤੀ",
        ]
        records = segment_page_texts(pages)

        self.assertEqual([record["source_ordinal"] for record in records], [1, 2, 3, 4])
        self.assertEqual(records[0]["source_page_start"], 2)
        self.assertEqual(records[0]["source_page_end"], 2)
        self.assertEqual(records[1]["source_page_start"], 2)
        self.assertEqual(records[1]["source_page_end"], 3)
        self.assertIn("ਦੂਜੀ ਜਾਰੀ", records[1]["source_text_extracted"])
        self.assertEqual(records[2]["source_page_end"], 3)
        self.assertNotIn("PunjabLibrary", records[2]["source_text_extracted"])
        self.assertEqual(records[2]["review_status"], "needs_review")

    def test_audit_reports_missing_duplicates_and_empty_text(self) -> None:
        records = [
            {"source_ordinal": 1, "title_gurmukhi_extracted": "one", "source_text_extracted": ""},
            {
                "source_ordinal": 1,
                "title_gurmukhi_extracted": "one",
                "source_text_extracted": "text",
            },
            {
                "source_ordinal": 3,
                "title_gurmukhi_extracted": "three",
                "source_text_extracted": "text",
            },
        ]
        audit = _audit(records, expected_count=3)
        self.assertEqual(audit["missing_ordinals"], [2])
        self.assertEqual(audit["duplicate_ordinals"], [1])
        self.assertEqual(audit["empty_texts"], 1)


if __name__ == "__main__":
    unittest.main()
