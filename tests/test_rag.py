from __future__ import annotations

import unittest

from abshaar.rag import compose_prompt, validate_citations


HITS = [
    {
        "id": "kb:bulleh_shah_0002:original",
        "text": "الف اللہ دل رتّا میرا",
        "metadata": {"kind": "original", "uncertainty": False},
        "score": 0.71,
    },
    {
        "id": "kb:bio_claim_bulleh_birthplace",
        "text": "Biographical claim (identity; evidence: multiple_later_sources): ...",
        "metadata": {"kind": "biographical_claim", "uncertainty": True},
        "score": 0.55,
    },
]


class RagTest(unittest.TestCase):
    def test_compose_prompt_numbers_records_and_flags_uncertainty(self) -> None:
        prompt = compose_prompt("What does Alif teach?", HITS)
        self.assertIn("Question: What does Alif teach?", prompt)
        self.assertIn("Record 1 — id kb:bulleh_shah_0002:original", prompt)
        self.assertIn("Record 2 — id kb:bio_claim_bulleh_birthplace", prompt)
        self.assertIn("[carries uncertainty qualifiers]", prompt)
        self.assertEqual(prompt.count("[carries uncertainty qualifiers]"), 1)

    def test_validate_citations_accepts_retrieved_ids(self) -> None:
        answer = "Alif is Allah [kb:bulleh_shah_0002:original]."
        self.assertEqual(validate_citations(answer, HITS), [])

    def test_validate_citations_flags_invented_ids(self) -> None:
        answer = "As shown [kb:bulleh_shah_0099:tashreeh] and [kb:bulleh_shah_0002:original]."
        self.assertEqual(validate_citations(answer, HITS), ["kb:bulleh_shah_0099:tashreeh"])


if __name__ == "__main__":
    unittest.main()
