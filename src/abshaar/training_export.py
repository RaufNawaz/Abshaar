"""Rights-safe export of trainable corpus layers.

This module is the firewall between the corpus and any training data: only
layers marked trainable are emitted, and every emitted text is scanned for
n-gram overlap with the copyrighted reference translations. A leak is a hard
failure, never a warning.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl, write_jsonl


LEAK_NGRAM_SIZE = 8

# Markers used across the corpus for uncertain readings. Review-note-level
# uncertainty is not serialized into poems.jsonl, so this layer-text scan is a
# lower bound, not an exhaustive uncertainty audit.
UNCERTAINTY_RE = re.compile(
    r"\[uncertain|\[torn|uncertain line|reading uncertain|high-uncertainty|\(\?\)",
    re.I,
)


def normalize_words(text: str) -> list[str]:
    return re.sub(r"[^\w\s]", " ", text.lower()).split()


def _ngrams(words: list[str], size: int) -> set[tuple[str, ...]]:
    return {tuple(words[i : i + size]) for i in range(len(words) - size + 1)}


def build_reference_index(reference_texts: list[str]) -> dict[str, Any]:
    ngrams: set[tuple[str, ...]] = set()
    short_texts: list[str] = []
    for text in reference_texts:
        words = normalize_words(text)
        if len(words) >= LEAK_NGRAM_SIZE:
            ngrams |= _ngrams(words, LEAK_NGRAM_SIZE)
        elif words:
            short_texts.append(" ".join(words))
    return {"ngrams": ngrams, "short_texts": short_texts}


def find_leaks(text: str, reference_index: dict[str, Any]) -> bool:
    words = normalize_words(text)
    if _ngrams(words, LEAK_NGRAM_SIZE) & reference_index["ngrams"]:
        return True
    joined = " ".join(words)
    return any(short and short in joined for short in reference_index["short_texts"])


def _is_uncertain(*texts: str) -> bool:
    return any(UNCERTAINTY_RE.search(text) for text in texts if text)


def extract_trainable_layers(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (trainable layer records, leak descriptions).

    Leak descriptions are non-empty only if an emitted layer overlaps a
    reference translation; callers must treat that as a fatal error.
    """
    reference_texts = [
        t.get("text", "")
        for record in records
        for t in record.get("translations", [])
        if isinstance(t, dict) and t.get("kind") == "reference_translation"
    ]
    reference_index = build_reference_index(reference_texts)

    layers: list[dict[str, Any]] = []
    for record in records:
        poem_id = record.get("id", "unknown")
        source_ids = record.get("source_ids", [])
        original_text = record.get("original", {}).get("text", "")

        def add(layer_id: str, kind: str, text: str, rights: str, created_by: str, model: str | None) -> None:
            if not text.strip():
                return
            layers.append(
                {
                    "record_id": layer_id,
                    "poem_id": poem_id,
                    "kind": kind,
                    "text": text,
                    "source_ids": source_ids,
                    "rights": rights,
                    "created_by": created_by,
                    "model": model,
                    "trainable": True,
                    "uncertainty": _is_uncertain(text, original_text),
                }
            )

        add(f"{poem_id}:original", "original", original_text, "public-domain", "source", None)
        add(
            f"{poem_id}:transliteration",
            "transliteration",
            record.get("transliteration", {}).get("text", ""),
            "project",
            "human",
            None,
        )
        for translation in record.get("translations", []):
            if not isinstance(translation, dict) or translation.get("trainable") is not True:
                continue
            add(
                translation.get("id", f"{poem_id}:translation"),
                translation.get("kind", "translation"),
                translation.get("text", ""),
                translation.get("rights", "project"),
                translation.get("created_by", "unknown"),
                translation.get("model"),
            )
        for tashreeh in record.get("tashreeh", []):
            if not isinstance(tashreeh, dict) or tashreeh.get("trainable") is not True:
                continue
            add(
                tashreeh.get("id", f"{poem_id}:tashreeh"),
                "tashreeh",
                tashreeh.get("text", ""),
                tashreeh.get("rights", "project"),
                tashreeh.get("created_by", "unknown"),
                tashreeh.get("model"),
            )

    leaks = [
        f"{layer['record_id']} ({layer['kind']}) shares an {LEAK_NGRAM_SIZE}-gram with a reference translation"
        for layer in layers
        if find_leaks(layer["text"], reference_index)
    ]
    return layers, leaks


def export_training_corpus(root: Path, output: Path) -> tuple[int, list[str]]:
    records = read_jsonl(root / "data" / "processed" / "poems.jsonl")
    layers, leaks = extract_trainable_layers(records)
    if leaks:
        return 0, leaks
    write_jsonl(output, layers)
    return len(layers), []
