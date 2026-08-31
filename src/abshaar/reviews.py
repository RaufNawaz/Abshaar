"""Human review corrections, and how they reach the corpus.

`data/annotations/reviews.jsonl` has had a schema since the project began
(`data/templates/reviews.template.jsonl`) but until 2026-08-31 nothing read
it: it was counted in `status.py` and schema-checked in `validation.py`, and
that was all. Writing a careful review changed nothing about what the model
trained on, which made the most valuable work in the project inert.

This module closes that loop. A review's `corrected_translation` and
`corrected_tashreeh` become corpus layers attributed to a human, and they
take precedence over the AI drafts for the same poem everywhere layers are
consumed — the knowledge base, the trainable export, and the training-data
generator.

Precedence is deliberately absolute: if a human has corrected a layer, the
AI version of that layer is not emitted at all. A corpus that emits both
teaches the model that they are interchangeable, which is the opposite of
the point.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl

REVIEWS_PATH = "data/annotations/reviews.jsonl"

# corrected_* -> the layer kind it supersedes
CORRECTION_FIELDS = {
    "corrected_translation": "literary_translation",
    "corrected_tashreeh": "tashreeh",
}

# A field left as the template's own placeholder, e.g. "[corrected translation]".
# Deliberately narrow: a real correction may legitimately contain bracketed
# uncertainty annotations such as "[uncertain line — torn]", and those must
# not be mistaken for an unfilled field.
_PLACEHOLDER_RE = re.compile(r"^\[[^\]]*\]$")


def _is_placeholder(text: str) -> bool:
    return bool(_PLACEHOLDER_RE.match(text.strip()))


def load_corrections(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    """Return {poem_id: {layer_kind: {"text", "reviewer", "review_id", "date"}}}.

    Only reviews naming a reviewer and carrying real corrected text count. A
    later review for the same poem and kind supersedes an earlier one, so the
    file can be appended to rather than edited in place.
    """
    corrections: dict[str, dict[str, dict[str, Any]]] = {}
    for review in read_jsonl(root / REVIEWS_PATH):
        poem_id = str(review.get("poem_id") or "").strip()
        reviewer = str(review.get("reviewer") or "").strip()
        if not poem_id or not reviewer or _is_placeholder(reviewer):
            continue
        for field, kind in CORRECTION_FIELDS.items():
            text = str(review.get(field) or "").strip()
            if not text or _is_placeholder(text):
                continue
            corrections.setdefault(poem_id, {})[kind] = {
                "text": text,
                "reviewer": reviewer,
                "review_id": str(review.get("id") or ""),
                "date": str(review.get("date") or ""),
            }
    return corrections


def apply_to_layers(
    layers: list[dict[str, Any]],
    corrections: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Replace AI layers with their human corrections, in place of, not beside."""
    if not corrections:
        return layers

    result: list[dict[str, Any]] = []
    replaced: set[tuple[str, str]] = set()
    for layer in layers:
        poem_id = str(layer.get("poem_id") or "")
        kind = str(layer.get("kind") or "")
        correction = corrections.get(poem_id, {}).get(kind)
        if correction is None:
            result.append(layer)
            continue
        superseded = layer.get("id")
        result.append(
            {
                **layer,
                "id": f"{poem_id}:{kind}:human",
                "text": correction["text"],
                "created_by": "human",
                "model": None,
                "reviewer": correction["reviewer"],
                "review_id": correction["review_id"],
                "supersedes": superseded,
            }
        )
        replaced.add((poem_id, kind))

    # A correction for a layer the entry never had still belongs in the corpus.
    for poem_id, kinds in sorted(corrections.items()):
        for kind, correction in sorted(kinds.items()):
            if (poem_id, kind) in replaced:
                continue
            result.append(
                {
                    "id": f"{poem_id}:{kind}:human",
                    "poem_id": poem_id,
                    "kind": kind,
                    "text": correction["text"],
                    "source_ids": [],
                    "rights": "project",
                    "created_by": "human",
                    "model": None,
                    "reviewer": correction["reviewer"],
                    "review_id": correction["review_id"],
                    "supersedes": None,
                    "trainable": True,
                    "uncertainty": False,
                }
            )
    return result


def correction_summary(corrections: dict[str, dict[str, dict[str, Any]]]) -> str:
    if not corrections:
        return "no human corrections found"
    by_kind: dict[str, int] = {}
    for kinds in corrections.values():
        for kind in kinds:
            by_kind[kind] = by_kind.get(kind, 0) + 1
    parts = ", ".join(f"{count} {kind}" for kind, count in sorted(by_kind.items()))
    return f"{len(corrections)} poem(s) with human corrections ({parts})"
