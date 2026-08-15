"""Mechanical extraction of Key Terms and Themes from working entries.

No content is generated here: headwords, meanings, and do_not_flatten_to
clauses are parsed verbatim from each entry's `# Key Terms` section and merged
across poems. Unknown fields stay empty rather than being invented.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from abshaar.jsonl import write_jsonl
from abshaar.markdown_entry import parse_markdown_entry
from abshaar.text import slugify
from abshaar.validation import iter_working_entries


DNFT_SEPARATOR = "do_not_flatten_to"


def parse_key_term_bullets(section_text: str) -> list[dict[str, str]]:
    terms: list[dict[str, str]] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        headword, meaning = stripped[2:].split(":", 1)
        headword, meaning = headword.strip(), meaning.strip()
        if not headword or not meaning or headword.startswith("["):
            continue
        do_not_flatten = ""
        if DNFT_SEPARATOR in meaning:
            meaning, do_not_flatten = meaning.split(DNFT_SEPARATOR, 1)
            meaning = meaning.rstrip().rstrip(";").rstrip()
            do_not_flatten = do_not_flatten.strip().rstrip(".").strip()
        terms.append({"headword": headword, "meaning": meaning, "do_not_flatten_to": do_not_flatten})
    return terms


def parse_theme_bullets(section_text: str) -> list[str]:
    themes: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        theme = stripped[2:].strip()
        if theme and not theme.startswith("["):
            themes.append(theme)
    return themes


def extract_lexicon(root: Path) -> dict[str, Any]:
    terms_by_id: dict[str, dict[str, Any]] = {}
    themes_by_id: dict[str, dict[str, Any]] = {}
    entries_without_terms: list[str] = []

    for path in iter_working_entries(root):
        entry = parse_markdown_entry(path)
        poem_id = str(entry.front_matter.get("id") or path.stem)
        poet_id = str(entry.front_matter.get("poet_id") or "unknown_poet")
        source_ids = entry.front_matter.get("source_ids") or []
        if isinstance(source_ids, str):
            source_ids = [source_ids]

        parsed_terms = parse_key_term_bullets(entry.sections.get("key_terms", ""))
        if not parsed_terms:
            entries_without_terms.append(poem_id)
        for parsed in parsed_terms:
            term_id = f"term_{slugify(parsed['headword'])}_{poet_id}"
            record = terms_by_id.setdefault(
                term_id,
                {
                    "id": term_id,
                    "headword": parsed["headword"],
                    "script_forms": [],
                    "transliteration": parsed["headword"],
                    "languages": [],
                    "basic_meaning": "",
                    "poet_specific_meaning": "",
                    "do_not_flatten_to": [],
                    "translation_policy": "",
                    "related_terms": [],
                    "example_poems": [],
                    "source_ids": [],
                    "review_status": "ai_draft",
                    "notes": "Extracted mechanically from entry Key Terms sections; AI-drafted content pending review.",
                },
            )
            per_poem = f"In {poem_id}: {parsed['meaning']}"
            record["poet_specific_meaning"] = (
                f"{record['poet_specific_meaning']} {per_poem}".strip()
            )
            if parsed["do_not_flatten_to"] and parsed["do_not_flatten_to"] not in record["do_not_flatten_to"]:
                record["do_not_flatten_to"].append(parsed["do_not_flatten_to"])
            if poem_id not in record["example_poems"]:
                record["example_poems"].append(poem_id)
            for source_id in source_ids:
                if source_id not in record["source_ids"]:
                    record["source_ids"].append(source_id)

        for theme in parse_theme_bullets(entry.sections.get("themes", "")):
            theme_id = theme if theme.startswith("theme_") else f"theme_{slugify(theme)}"
            label_source = theme_id.removeprefix("theme_")
            record = themes_by_id.setdefault(
                theme_id,
                {
                    "id": theme_id,
                    "label": label_source.replace("_", " ").capitalize(),
                    "summary": "",
                    "related_terms": [],
                    "example_poems": [],
                    "source_ids": [],
                    "review_status": "ai_draft",
                },
            )
            if poem_id not in record["example_poems"]:
                record["example_poems"].append(poem_id)
            for source_id in source_ids:
                if source_id not in record["source_ids"]:
                    record["source_ids"].append(source_id)

    terms = [terms_by_id[key] for key in sorted(terms_by_id)]
    themes = [themes_by_id[key] for key in sorted(themes_by_id)]
    write_jsonl(root / "data" / "lexicon" / "terms.jsonl", terms)
    write_jsonl(root / "data" / "context" / "themes.jsonl", themes)
    return {
        "terms": len(terms),
        "themes": len(themes),
        "entries_without_terms": entries_without_terms,
    }
