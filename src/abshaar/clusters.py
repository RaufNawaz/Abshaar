"""Conservative canonical-work clustering.

Deliberately over-fragments rather than over-merges: only crosswalk candidates
with a perfect 1.0 score join a cluster automatically — but ALL 1.0-score
candidates of a witness merge (a witness exactly matching two entries proves
those entries are witnesses of one work; keeping them apart would let variants
leak across train/eval splits). Everything below 1.0 stays separate with
cluster_confidence "unreviewed" and is recorded as a related candidate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl, write_jsonl


RELATED_CANDIDATE_THRESHOLD = 0.85


def _load(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path) if path.exists() else []


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, member: str) -> None:
        self.parent.setdefault(member, member)

    def find(self, member: str) -> str:
        while self.parent[member] != member:
            self.parent[member] = self.parent[self.parent[member]]
            member = self.parent[member]
        return member

    def union(self, a: str, b: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            # Deterministic: the lexicographically smaller root wins.
            keep, drop = sorted((root_a, root_b))
            self.parent[drop] = keep


def build_clusters(root: Path) -> dict[str, int]:
    poems = _load(root / "data" / "processed" / "poems.jsonl")
    match_files = {
        "sufinama_kaafi_witness": _load(root / "data" / "context" / "source_matches.jsonl"),
        "sufinama_text_witness": _load(root / "data" / "context" / "sufinama_text_source_matches.jsonl"),
    }
    punjab_items = _load(root / "data" / "context" / "punjab_library_source_items.jsonl")

    member_types: dict[str, str] = {}
    uf = _UnionFind()
    for poem in poems:
        poem_id = str(poem.get("id"))
        member_types[poem_id] = "entry"
        uf.add(poem_id)
    for item in punjab_items:
        item_id = str(item.get("id"))
        member_types[item_id] = "punjab_library_witness"
        uf.add(item_id)

    related: dict[str, list[dict[str, Any]]] = {}
    auto_merged = 0
    for member_type, matches in match_files.items():
        for match in matches:
            item_id = str(match.get("source_item_id"))
            member_types[item_id] = member_type
            uf.add(item_id)
            candidates = match.get("candidate_poems") or []
            exact = [
                c
                for c in candidates
                if c.get("score") == 1.0 and str(c.get("poem_id")) in member_types
            ]
            for candidate in exact:
                uf.union(item_id, str(candidate["poem_id"]))
            if exact:
                auto_merged += 1
            related[item_id] = [
                {
                    "member_id": str(c.get("poem_id")),
                    "score": c.get("score"),
                    "relation": "crosswalk_candidate_not_merged",
                }
                for c in candidates
                if c not in exact and (c.get("score") or 0) >= RELATED_CANDIDATE_THRESHOLD
            ]

    groups: dict[str, list[str]] = {}
    for member in member_types:
        groups.setdefault(uf.find(member), []).append(member)

    records = []
    for members in groups.values():
        members.sort()
        entry_members = [m for m in members if member_types[m] == "entry"]
        anchor = entry_members[0] if entry_members else members[0]
        work_id = f"work_{anchor}"
        cluster_related = []
        seen_related = set()
        for member in members:
            for candidate in related.get(member, []):
                key = (candidate["member_id"], candidate["score"])
                if key not in seen_related and candidate["member_id"] not in members:
                    seen_related.add(key)
                    cluster_related.append(candidate)
        notes = ""
        if member_types[members[0]] == "punjab_library_witness":
            notes = "Gurmukhi heading unverified against page images; never auto-merge."
        records.append(
            {
                "id": work_id,
                "canonical_work_id": work_id,
                "members": [
                    {
                        "member_id": member,
                        "member_type": member_types[member],
                        "role": "anchor" if member == anchor else "witness",
                    }
                    for member in members
                ],
                "cluster_confidence": "auto_exact_match" if len(members) > 1 else "unreviewed",
                "related_candidates": cluster_related,
                "method": "conservative_auto_v1",
                "notes": notes,
            }
        )

    records.sort(key=lambda record: record["id"])
    write_jsonl(root / "data" / "context" / "canonical_clusters.jsonl", records)
    return {
        "clusters": len(records),
        "members": sum(len(record["members"]) for record in records),
        "auto_merged_witnesses": auto_merged,
    }


def cluster_map(root: Path) -> dict[str, str]:
    """member_id -> canonical_work_id, from the generated cluster file."""
    mapping: dict[str, str] = {}
    for cluster in _load(root / "data" / "context" / "canonical_clusters.jsonl"):
        for member in cluster.get("members", []):
            mapping[str(member.get("member_id"))] = str(cluster.get("canonical_work_id"))
    return mapping
