from __future__ import annotations

from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl, write_json


SYSTEM_PROMPT = """You assist with a scholarly but beginner-friendly translation of classical South Asian mystical poetry.

Rules:
1. Preserve the original image before explaining it.
2. Separate literal gloss, literary translation, and tashreeh.
3. Do not invent biography, doctrine, source claims, or historical context.
4. Use retrieved context only when relevant.
5. Mark uncertainty and alternate readings.
6. If a term should remain untranslated, say so.
7. Keep the answer useful for a new reader without flattening the tradition.
"""


def _by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record.get("id")): record for record in records if record.get("id")}


def build_prompt_pack(root: Path, poem_id: str) -> dict[str, Any]:
    poems = read_jsonl(root / "data" / "processed" / "poems.jsonl")
    poem = next((item for item in poems if item.get("id") == poem_id), None)
    if poem is None:
        raise ValueError(f"poem `{poem_id}` not found in data/processed/poems.jsonl")

    terms_by_id = _by_id(read_jsonl(root / "data" / "lexicon" / "terms.jsonl"))
    themes_by_id = _by_id(read_jsonl(root / "data" / "context" / "themes.jsonl"))
    people_by_id = _by_id(read_jsonl(root / "data" / "context" / "people.jsonl"))

    glossary = [
        terms_by_id[term_id]
        for term_id in poem.get("glossary_terms", [])
        if term_id in terms_by_id
    ]
    themes = [
        themes_by_id[theme_id]
        for theme_id in poem.get("themes", [])
        if theme_id in themes_by_id
    ]
    poet = people_by_id.get(str(poem.get("poet_id")))

    user_prompt = f"""Poet:
{poem.get("poet_id")}

Original:
{poem.get("original", {}).get("text", "")}

Transliteration:
{poem.get("transliteration", {}).get("text", "")}

Existing literal gloss:
{_translation_text(poem, "literal_gloss")}

Existing literary translation:
{_translation_text(poem, "literary_translation")}

Existing tashreeh:
{_tashreeh_text(poem)}

Retrieved poet context:
{poet or {}}

Retrieved glossary:
{glossary}

Retrieved themes:
{themes}

Return JSON with these fields:
literal_gloss, direct_translation, literary_translation, tashreeh_beginner,
tashreeh_advanced, key_terms, alternate_readings, uncertainty_notes,
retrieved_context_used.
"""

    return {
        "poem_id": poem_id,
        "model": "qwen3:8b",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "context_ids": {
            "poet": poem.get("poet_id") if poet else None,
            "glossary_terms": [item.get("id") for item in glossary],
            "themes": [item.get("id") for item in themes],
        },
    }


def save_prompt_pack(root: Path, poem_id: str) -> Path:
    pack = build_prompt_pack(root, poem_id)
    output_path = root / "data" / "cache" / "prompt_packs" / f"{poem_id}.json"
    write_json(output_path, pack)
    return output_path


def _translation_text(poem: dict[str, Any], kind: str) -> str:
    for item in poem.get("translations", []):
        if isinstance(item, dict) and item.get("kind") == kind:
            return str(item.get("text") or "")
    return ""


def _tashreeh_text(poem: dict[str, Any]) -> str:
    values = [
        str(item.get("text") or "")
        for item in poem.get("tashreeh", [])
        if isinstance(item, dict)
    ]
    return "\n\n".join(value for value in values if value.strip())
