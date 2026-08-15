from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from abshaar.clusters import build_clusters, cluster_map
from abshaar.knowledge_base import witness_view_text
from abshaar.lexicon import parse_key_term_bullets, parse_theme_bullets


KEY_TERMS_SECTION = """
- Alif: the first letter as cipher of Allah; do_not_flatten_to a mere alphabet letter.
- khoṭ / suchiār: "false within, upright without"; do_not_flatten_to simple two-facedness.
- plainterm: a meaning without the flatten clause.
- [ishq]:
- emptyterm:
"""

THEMES_SECTION = """
- divine_unity
- theme_ritual_critique
- [placeholder_theme]
"""


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


class LexiconParsingTest(unittest.TestCase):
    def test_key_terms_parse_meanings_and_flatten_clauses(self) -> None:
        terms = parse_key_term_bullets(KEY_TERMS_SECTION)
        by_head = {t["headword"]: t for t in terms}
        self.assertEqual(set(by_head), {"Alif", "khoṭ / suchiār", "plainterm"})
        self.assertEqual(by_head["Alif"]["do_not_flatten_to"], "a mere alphabet letter")
        self.assertEqual(by_head["Alif"]["meaning"], "the first letter as cipher of Allah")
        self.assertEqual(by_head["plainterm"]["do_not_flatten_to"], "")

    def test_theme_bullets_skip_placeholders(self) -> None:
        self.assertEqual(
            parse_theme_bullets(THEMES_SECTION), ["divine_unity", "theme_ritual_critique"]
        )


class ClustersTest(unittest.TestCase):
    def _make_root(self) -> Path:
        root = Path(self._tmp.name)
        _write_jsonl(
            root / "data/processed/poems.jsonl",
            [{"id": "bulleh_shah_0001"}, {"id": "bulleh_shah_0002"}],
        )
        _write_jsonl(
            root / "data/context/source_matches.jsonl",
            [
                {
                    "source_item_id": "sufinama_exact",
                    "candidate_poems": [
                        {"poem_id": "bulleh_shah_0001", "score": 1.0},
                        {"poem_id": "bulleh_shah_0002", "score": 0.9},
                    ],
                },
                {
                    "source_item_id": "sufinama_partial",
                    "candidate_poems": [{"poem_id": "bulleh_shah_0002", "score": 0.95}],
                },
            ],
        )
        _write_jsonl(
            root / "data/context/punjab_library_source_items.jsonl",
            [{"id": "punjab_library_bulleh_kafi_0001"}],
        )
        return root

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_only_exact_matches_merge(self) -> None:
        root = self._make_root()
        counts = build_clusters(root)
        self.assertEqual(counts["auto_merged_witnesses"], 1)
        # 2 poems + 1 singleton witness + 1 punjab item; exact witness merged into a poem cluster
        self.assertEqual(counts["clusters"], 4)
        self.assertEqual(counts["members"], 5)

        mapping = cluster_map(root)
        self.assertEqual(mapping["sufinama_exact"], mapping["bulleh_shah_0001"])
        self.assertNotEqual(mapping["sufinama_partial"], mapping["bulleh_shah_0002"])

    def test_witness_with_two_exact_candidates_merges_both_poems(self) -> None:
        root = self._make_root()
        _write_jsonl(
            root / "data/context/source_matches.jsonl",
            [
                {
                    "source_item_id": "sufinama_double_exact",
                    "candidate_poems": [
                        {"poem_id": "bulleh_shah_0001", "score": 1.0},
                        {"poem_id": "bulleh_shah_0002", "score": 1.0},
                    ],
                }
            ],
        )
        build_clusters(root)
        mapping = cluster_map(root)
        self.assertEqual(mapping["bulleh_shah_0001"], mapping["bulleh_shah_0002"])
        self.assertEqual(mapping["sufinama_double_exact"], mapping["bulleh_shah_0001"])

    def test_deterministic_rerun(self) -> None:
        root = self._make_root()
        build_clusters(root)
        first = (root / "data/context/canonical_clusters.jsonl").read_text(encoding="utf-8")
        build_clusters(root)
        second = (root / "data/context/canonical_clusters.jsonl").read_text(encoding="utf-8")
        self.assertEqual(first, second)


class WitnessViewTextTest(unittest.TestCase):
    def test_tokens_join_into_lines(self) -> None:
        view = {
            "lines": [
                {"tokens": [{"text": "ranjha"}, {"text": "ranjha"}, {"text": "kardi"}]},
                {"tokens": [{"text": ""}]},
                {"tokens": [{"text": "ve"}, {"text": "main"}]},
            ]
        }
        self.assertEqual(witness_view_text(view), "ranjha ranjha kardi\nve main")


if __name__ == "__main__":
    unittest.main()
