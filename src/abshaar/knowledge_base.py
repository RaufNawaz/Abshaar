"""Consolidated knowledge base for retrieval and training-data generation.

One record per atomic fact, each with provenance, rights, and uncertainty.
Contains Sufinama witness text (private research authorization), so the
output lives under data/processed/private/. Every record is leak-scanned
against the copyrighted reference translations; a hit aborts the build.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from abshaar.clusters import cluster_map
from abshaar.jsonl import read_jsonl, write_jsonl
from abshaar.training_export import (
    build_reference_index,
    extract_trainable_layers,
    find_leaks,
)


KB_PATH = "data/processed/private/knowledge_base.jsonl"


def _load(root: Path, relative: str) -> list[dict[str, Any]]:
    path = root / relative
    return read_jsonl(path) if path.exists() else []


def witness_view_text(view: dict[str, Any]) -> str:
    lines_out: list[str] = []
    for line in view.get("lines", []):
        tokens = [str(t.get("text", "")) for t in line.get("tokens", [])]
        joined = " ".join(token for token in tokens if token)
        if joined.strip():
            lines_out.append(joined)
    return "\n".join(lines_out)


def build_kb(root: Path, include_reference: bool = False) -> tuple[dict[str, int], list[str]]:
    poems = _load(root, "data/processed/poems.jsonl")
    works = cluster_map(root)
    records: list[dict[str, Any]] = []

    def add(
        kb_id: str,
        kind: str,
        text: str,
        poem_ids: list[str],
        source_ids: list[str],
        rights: str,
        trainable: bool,
        uncertainty: bool,
        provenance_note: str,
    ) -> None:
        if not text.strip():
            return
        anchor = poem_ids[0] if poem_ids else ""
        records.append(
            {
                "id": kb_id,
                "kind": kind,
                "text": text,
                "poem_ids": poem_ids,
                "canonical_work_id": works.get(anchor, ""),
                "source_ids": source_ids,
                "rights": rights,
                "trainable": trainable,
                "uncertainty": uncertainty,
                "provenance_note": provenance_note,
            }
        )

    layers, layer_leaks = extract_trainable_layers(poems, include_reference=include_reference)
    if layer_leaks:
        return {}, layer_leaks
    for layer in layers:
        add(
            f"kb:{layer['id']}",
            layer["kind"],
            layer["text"],
            [layer["poem_id"]],
            layer["source_ids"],
            layer["rights"],
            True,
            layer["uncertainty"],
            f"Layer of working entry {layer['poem_id']} (created_by {layer['created_by']}).",
        )

    for term in _load(root, "data/lexicon/terms.jsonl"):
        dnft = "; ".join(term.get("do_not_flatten_to", []))
        text = f"Term: {term.get('headword')}. {term.get('poet_specific_meaning', '')}"
        if dnft:
            text += f" Do not flatten to: {dnft}."
        add(
            f"kb:{term['id']}",
            "term",
            text,
            term.get("example_poems", []),
            term.get("source_ids", []),
            "project",
            True,
            False,
            "Extracted from entry Key Terms sections; AI-drafted, pending review.",
        )

    for theme in _load(root, "data/context/themes.jsonl"):
        poems_list = ", ".join(theme.get("example_poems", []))
        add(
            f"kb:{theme['id']}",
            "theme",
            f"Theme: {theme.get('label')}. Appears in: {poems_list}.",
            theme.get("example_poems", []),
            theme.get("source_ids", []),
            "project",
            True,
            False,
            "Extracted from entry Themes sections; AI-drafted, pending review.",
        )

    for claim in _load(root, "data/context/biographical_claims.jsonl"):
        text = (
            f"Biographical claim ({claim.get('claim_type')}; evidence: {claim.get('evidence_status')}; "
            f"confidence: {claim.get('confidence')}): {claim.get('claim')}"
        )
        if claim.get("caution"):
            text += f" Caution: {claim['caution']}"
        add(
            f"kb:{claim['id']}",
            "biographical_claim",
            text,
            [],
            claim.get("source_ids", []),
            "project",
            True,
            True,
            "Claim-level biography record; evidence qualifiers are part of the fact.",
        )

    for event in _load(root, "data/context/events.jsonl"):
        add(
            f"kb:{event['id']}",
            "event",
            f"Event ({event.get('date_label')}): {event.get('title')}. {event.get('description', '')}",
            [],
            event.get("source_ids", []),
            "project",
            True,
            "disputed" in str(event.get("date_label", "")).lower()
            or str(event.get("confidence", "")).lower() in {"low", "disputed"},
            "Timeline event; date_label carries the dating caution verbatim.",
        )

    for source in _load(root, "data/context/sources.jsonl"):
        add(
            f"kb:{source['id']}",
            "source",
            f"Source {source.get('id')}: {source.get('title')} — {source.get('author_or_editor')}, "
            f"{source.get('publisher')}, {source.get('year')}. {source.get('url', '')}",
            [],
            [str(source.get("id"))],
            "project",
            False,
            False,
            "Bibliographic metadata; not training text.",
        )

    witness_files = {
        "sufinama_kaafi_witness": "data/processed/private/sufinama_bulleh_shah_kaafi.jsonl",
        "sufinama_text_witness": "data/processed/private/sufinama_bulleh_shah_other_texts.jsonl",
    }
    for kind, relative in witness_files.items():
        for witness in _load(root, relative):
            witness_id = str(witness.get("id"))
            title = witness.get("catalog_title_roman") or witness.get("catalog_title") or ""
            work_id = works.get(witness_id, "")
            linked_poems = sorted(
                {
                    m
                    for m, w in works.items()
                    if work_id and w == work_id and m.startswith("bulleh_shah_")
                }
            )
            for view_name, view in (witness.get("views") or {}).items():
                text = witness_view_text(view if isinstance(view, dict) else {})
                if not text:
                    continue
                records.append(
                    {
                        "id": f"kb:{witness_id}:{view_name}",
                        "kind": kind,
                        "text": text,
                        "poem_ids": linked_poems,
                        "canonical_work_id": work_id,
                        "source_ids": [str(witness.get("source_id"))],
                        "rights": "sufinama_private_research",
                        "trainable": True,
                        "uncertainty": False,
                        "provenance_note": f"Sufinama witness {witness_id} view {view_name}; catalog title: {title}.",
                    }
                )

    for cluster in _load(root, "data/context/canonical_clusters.jsonl"):
        members = cluster.get("members", [])
        if len(members) < 2:
            continue
        member_desc = ", ".join(f"{m['member_id']} ({m['member_type']})" for m in members)
        add(
            f"kb:{cluster['id']}:relation",
            "cluster_relation",
            f"These records are witnesses of one work ({cluster.get('cluster_confidence')}): {member_desc}.",
            [m["member_id"] for m in members if str(m["member_id"]).startswith("bulleh_shah_")],
            [],
            "project",
            True,
            cluster.get("cluster_confidence") != "auto_exact_match",
            "Automatically clustered; only exact 1.0 crosswalk matches are merged.",
        )

    if not include_reference:
        reference_index = build_reference_index(
            [
                t.get("text", "")
                for poem in poems
                for t in poem.get("translations", [])
                if isinstance(t, dict) and t.get("kind") == "reference_translation"
            ]
        )
        leaks = [
            f"{record['id']} ({record['kind']}) shares an 8-gram with a reference translation"
            for record in records
            if find_leaks(record["text"], reference_index)
        ]
        if leaks:
            return {}, leaks

    write_jsonl(root / KB_PATH, records)
    counts: dict[str, int] = {}
    for record in records:
        counts[record["kind"]] = counts.get(record["kind"], 0) + 1
    counts["total"] = len(records)
    return counts, []
