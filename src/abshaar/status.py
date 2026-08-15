from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl
from abshaar.validation import iter_working_entries, validate_project


def _safe_read(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path) if path.exists() else []


def project_status(root: Path) -> dict[str, Any]:
    poems = _safe_read(root / "data" / "processed" / "poems.jsonl")
    terms = _safe_read(root / "data" / "lexicon" / "terms.jsonl")
    sources = _safe_read(root / "data" / "context" / "sources.jsonl")
    people = _safe_read(root / "data" / "context" / "people.jsonl")
    events = _safe_read(root / "data" / "context" / "events.jsonl")
    themes = _safe_read(root / "data" / "context" / "themes.jsonl")
    reviews = _safe_read(root / "data" / "annotations" / "reviews.jsonl")
    model_outputs = _safe_read(root / "data" / "annotations" / "model_outputs.jsonl")
    source_matches = _safe_read(root / "data" / "context" / "source_matches.jsonl")
    source_items = _safe_read(root / "data" / "context" / "sufinama_source_items.jsonl")
    sufinama_text_items = _safe_read(
        root / "data" / "context" / "sufinama_text_source_items.jsonl"
    )
    sufinama_text_matches = _safe_read(
        root / "data" / "context" / "sufinama_text_source_matches.jsonl"
    )
    gurmukhi_source_items = _safe_read(
        root / "data" / "context" / "punjab_library_source_items.jsonl"
    )
    biographical_claims = _safe_read(root / "data" / "context" / "biographical_claims.jsonl")
    sufinama_inventory = _safe_read(
        root / "data" / "context" / "sufinama_bulleh_shah_inventory.jsonl"
    )
    clusters = _safe_read(root / "data" / "context" / "canonical_clusters.jsonl")
    kb_records = _safe_read(root / "data" / "processed" / "private" / "knowledge_base.jsonl")
    trainable_layers = _safe_read(root / "data" / "processed" / "training" / "trainable_layers.jsonl")
    train_examples = _safe_read(root / "data" / "processed" / "training" / "train.jsonl")
    eval_examples = _safe_read(root / "data" / "processed" / "training" / "eval.jsonl")
    probes = _safe_read(root / "data" / "processed" / "training" / "probes.jsonl")
    issues = validate_project(root)

    return {
        "working_entries": len(iter_working_entries(root)),
        "processed_poems": len(poems),
        "public_poems": sum(
            1 for poem in poems if poem.get("publication", {}).get("include_on_website") is True
        ),
        "glossary_terms": len(terms),
        "sources": len(sources),
        "people": len(people),
        "events": len(events),
        "themes": len(themes),
        "reviews": len(reviews),
        "model_outputs": len(model_outputs),
        "source_matches": len(source_matches),
        "source_items": len(source_items),
        "sufinama_text_items": len(sufinama_text_items),
        "sufinama_text_matches": len(sufinama_text_matches),
        "gurmukhi_source_items": len(gurmukhi_source_items),
        "biographical_claims": len(biographical_claims),
        "sufinama_inventory_categories": len(sufinama_inventory),
        "canonical_clusters": len(clusters),
        "multi_member_clusters": sum(1 for c in clusters if len(c.get("members", [])) > 1),
        "knowledge_base_records": len(kb_records),
        "trainable_layers": len(trainable_layers),
        "training_examples": len(train_examples) + len(eval_examples),
        "eval_examples": len(eval_examples),
        "eval_probes": len(probes),
        "validation_errors": sum(1 for issue in issues if issue.level == "error"),
        "validation_warnings": sum(1 for issue in issues if issue.level == "warning"),
    }


def format_project_status(status: dict[str, Any]) -> str:
    lines = [
        "Abshaar project status",
        "",
        f"Working Markdown entries: {status['working_entries']}",
        f"Processed poem records: {status['processed_poems']}",
        f"Poems marked public for website: {status['public_poems']}",
        f"Glossary terms: {status['glossary_terms']}",
        f"Sources: {status['sources']}",
        f"People records: {status['people']}",
        f"Timeline events: {status['events']}",
        f"Themes: {status['themes']}",
        f"Human reviews: {status['reviews']}",
        f"Model outputs awaiting review or archive: {status['model_outputs']}",
        f"Source-manifest matches awaiting review: {status['source_matches']}",
        f"Sufinama catalog source items: {status['source_items']}",
        f"Sufinama non-kaafi text source items: {status['sufinama_text_items']}",
        f"Sufinama non-kaafi matches awaiting review: {status['sufinama_text_matches']}",
        f"PunjabLibrary Gurmukhi source items: {status['gurmukhi_source_items']}",
        f"Sourced biographical claims: {status['biographical_claims']}",
        f"Sufinama Bulleh Shah inventory categories: {status['sufinama_inventory_categories']}",
        "",
        f"Canonical work clusters: {status['canonical_clusters']} ({status['multi_member_clusters']} multi-member)",
        f"Knowledge-base records (private): {status['knowledge_base_records']}",
        f"Rights-safe trainable layers: {status['trainable_layers']}",
        f"Training examples (train+eval): {status['training_examples']} ({status['eval_examples']} eval)",
        f"Evaluation probes: {status['eval_probes']}",
        "",
        f"Validation errors: {status['validation_errors']}",
        f"Validation warnings: {status['validation_warnings']}",
    ]
    return "\n".join(lines)


def next_poem_id(root: Path, poet_id: str) -> str:
    pattern = re.compile(rf"^{re.escape(poet_id)}_(\d+)$")
    numbers: list[int] = []

    for path in iter_working_entries(root):
        match = pattern.match(path.stem)
        if match:
            numbers.append(int(match.group(1)))

    for poem in _safe_read(root / "data" / "processed" / "poems.jsonl"):
        poem_id = str(poem.get("id") or "")
        match = pattern.match(poem_id)
        if match:
            numbers.append(int(match.group(1)))

    next_number = max(numbers, default=0) + 1
    return f"{poet_id}_{next_number:04d}"
