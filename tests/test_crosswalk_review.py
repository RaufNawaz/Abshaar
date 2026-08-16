import json
import tempfile
import unittest
from pathlib import Path

from abshaar.crosswalk_review import (
    _best_channel,
    _channel_evidence,
    _proposal,
    apply_crosswalk_classifications,
    CORPORA,
    CLASSIFICATIONS_PATH,
)
from abshaar.jsonl import read_jsonl, write_jsonl


def _pairs(*lines):
    return [{"raw": line, "key": line.replace(" ", "").lower()} for line in lines]


class ChannelEvidenceTests(unittest.TestCase):
    def test_identical_lines_give_full_coverage_and_exact_matches(self):
        witness = _pairs("ranjha ranjha kardi ni", "saddo ni mainun")
        evidence = _channel_evidence(witness, list(witness), "roman")
        self.assertEqual(evidence["witness_coverage_strong"], 1.0)
        self.assertEqual(evidence["entry_coverage_strong"], 1.0)
        self.assertEqual(evidence["exact_line_matches"], 2)

    def test_disjoint_lines_give_zero_coverage(self):
        evidence = _channel_evidence(
            _pairs("hori khelungi kah kar bismillah"),
            _pairs("uth chale gvandhon yar"),
            "roman",
        )
        self.assertEqual(evidence["witness_coverage_loose"], 0.0)
        self.assertEqual(evidence["entry_coverage_loose"], 0.0)
        self.assertEqual(evidence["exact_line_matches"], 0)

    def test_devanagari_channel_uses_softer_loose_threshold(self):
        witness = [{"raw": "x", "key": "munhaibaatnarahndiae"}]
        entry = [{"raw": "y", "key": "munhaibatnahrahndiaex"}]
        strict = _channel_evidence(witness, entry, "roman")
        soft = _channel_evidence(witness, entry, "devanagari")
        self.assertGreaterEqual(
            soft["witness_coverage_loose"], strict["witness_coverage_loose"]
        )

    def test_best_channel_prefers_higher_strong_coverage(self):
        low = _channel_evidence(_pairs("aaa bbb"), _pairs("zzz yyy"), "roman")
        high = _channel_evidence(_pairs("aaa bbb"), _pairs("aaa bbb"), "urdu")
        self.assertEqual(_best_channel([low, high])["channel"], "urdu")


class ProposalTests(unittest.TestCase):
    def _evidence(self, w_strong, e_strong, w_loose, e_loose, exact=0):
        return {
            "witness_coverage_strong": w_strong,
            "entry_coverage_strong": e_strong,
            "witness_coverage_loose": w_loose,
            "entry_coverage_loose": e_loose,
            "exact_line_matches": exact,
        }

    def test_no_channel_is_unmatched(self):
        self.assertEqual(_proposal(None), "unmatched")

    def test_zero_coverage_is_unmatched(self):
        self.assertEqual(_proposal(self._evidence(0, 0, 0, 0)), "unmatched")

    def test_full_bidirectional_strong_is_exact(self):
        self.assertEqual(_proposal(self._evidence(1.0, 0.95, 1.0, 1.0)), "exact_witness")

    def test_two_way_loose_is_variant(self):
        self.assertEqual(_proposal(self._evidence(0.4, 0.3, 0.8, 0.9)), "variant")

    def test_one_sided_containment_is_excerpt(self):
        self.assertEqual(_proposal(self._evidence(0.9, 0.2, 0.9, 0.3)), "excerpt")

    def test_partial_overlap_is_possible(self):
        self.assertEqual(_proposal(self._evidence(0.0, 0.0, 0.4, 0.2)), "possible")


class ApplyClassificationsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        kaafi_path = self.root / CORPORA[0][1]
        text_path = self.root / CORPORA[1][1]
        write_jsonl(
            kaafi_path,
            [
                {
                    "id": "source_match_sufinama_aaa",
                    "source_item_id": "sufinama_aaa",
                    "candidate_poems": [{"poem_id": "bulleh_shah_0001", "score": 1.0}],
                    "match_status": "needs_review",
                    "notes": "Candidate match only.",
                }
            ],
        )
        write_jsonl(
            text_path,
            [
                {
                    "id": "source_match_sufinama_text_doha_bbb",
                    "source_item_id": "sufinama_text_doha_bbb",
                    "candidate_poems": [{"poem_id": "bulleh_shah_0002", "score": 0.5}],
                    "match_status": "needs_review",
                    "notes": "Candidate match only.",
                }
            ],
        )
        self.kaafi_path = kaafi_path
        self.class_path = self.root / CLASSIFICATIONS_PATH

    def tearDown(self):
        self._tmp.cleanup()

    def _write_classifications(self, records):
        write_jsonl(self.class_path, records)

    def _good_records(self):
        return [
            {
                "match_id": "source_match_sufinama_aaa",
                "status": "exact_witness",
                "poem_id": "bulleh_shah_0001",
                "note": "full bidirectional coverage",
                "classified_by": "test",
                "classified_on": "2026-08-16",
            },
            {
                "match_id": "source_match_sufinama_text_doha_bbb",
                "status": "unmatched",
                "poem_id": None,
                "note": "zero coverage",
                "classified_by": "test",
                "classified_on": "2026-08-16",
            },
        ]

    def test_happy_path_applies_and_is_idempotent(self):
        self._write_classifications(self._good_records())
        counts = apply_crosswalk_classifications(self.root)
        self.assertEqual(counts["exact_witness"], 1)
        self.assertEqual(counts["unmatched"], 1)
        first = self.kaafi_path.read_bytes()
        apply_crosswalk_classifications(self.root)
        self.assertEqual(first, self.kaafi_path.read_bytes())
        record = read_jsonl(self.kaafi_path)[0]
        self.assertEqual(record["match_status"], "exact_witness")
        self.assertFalse(record["match_review"]["human_confirmed"])

    def test_rejects_unknown_status(self):
        records = self._good_records()
        records[0]["status"] = "definitely_same"
        self._write_classifications(records)
        with self.assertRaises(ValueError):
            apply_crosswalk_classifications(self.root)

    def test_rejects_missing_record(self):
        self._write_classifications(self._good_records()[:1])
        with self.assertRaises(ValueError):
            apply_crosswalk_classifications(self.root)

    def test_rejects_poem_id_outside_candidates(self):
        records = self._good_records()
        records[0]["poem_id"] = "bulleh_shah_0072"
        self._write_classifications(records)
        with self.assertRaises(ValueError):
            apply_crosswalk_classifications(self.root)

    def test_rejects_unmatched_with_poem_id(self):
        records = self._good_records()
        records[1]["poem_id"] = "bulleh_shah_0002"
        self._write_classifications(records)
        with self.assertRaises(ValueError):
            apply_crosswalk_classifications(self.root)

    def test_rejects_unknown_match_id_and_leaves_files_untouched(self):
        records = self._good_records()
        records.append(dict(records[0], match_id="source_match_sufinama_zzz"))
        self._write_classifications(records)
        before = self.kaafi_path.read_bytes()
        with self.assertRaises(ValueError):
            apply_crosswalk_classifications(self.root)
        self.assertEqual(before, self.kaafi_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
