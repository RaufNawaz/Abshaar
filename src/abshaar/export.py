from __future__ import annotations

from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl, write_json


def _safe_read(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path) if path.exists() else []


def export_site_data(root: Path) -> dict[str, int]:
    poems = _safe_read(root / "data" / "processed" / "poems.jsonl")
    terms = _safe_read(root / "data" / "lexicon" / "terms.jsonl")
    people = _safe_read(root / "data" / "context" / "people.jsonl")
    events = _safe_read(root / "data" / "context" / "events.jsonl")
    themes = _safe_read(root / "data" / "context" / "themes.jsonl")
    sources = _safe_read(root / "data" / "context" / "sources.jsonl")

    public_poems = [
        poem for poem in poems if poem.get("publication", {}).get("include_on_website") is True
    ]

    search_documents = []
    for poem in public_poems:
        translations = " ".join(
            item.get("text", "") for item in poem.get("translations", []) if isinstance(item, dict)
        )
        explanations = " ".join(
            item.get("text", "") for item in poem.get("tashreeh", []) if isinstance(item, dict)
        )
        search_documents.append(
            {
                "id": poem.get("id"),
                "type": "poem",
                "title": poem.get("title"),
                "poet_id": poem.get("poet_id"),
                "text": "\n".join(
                    [
                        poem.get("title", ""),
                        poem.get("original", {}).get("text", ""),
                        poem.get("transliteration", {}).get("text", ""),
                        translations,
                        explanations,
                    ]
                ).strip(),
            }
        )

    for term in terms:
        search_documents.append(
            {
                "id": term.get("id"),
                "type": "glossary_term",
                "title": term.get("headword"),
                "poet_id": None,
                "text": " ".join(
                    str(term.get(key, ""))
                    for key in ["headword", "transliteration", "basic_meaning", "poet_specific_meaning"]
                ).strip(),
            }
        )

    output_dir = root / "data" / "site"
    write_json(output_dir / "poems.json", public_poems)
    write_json(output_dir / "glossary.json", terms)
    write_json(output_dir / "people.json", people)
    write_json(output_dir / "events.json", events)
    write_json(output_dir / "themes.json", themes)
    write_json(output_dir / "sources.json", sources)
    write_json(output_dir / "search_documents.json", search_documents)

    return {
        "public_poems": len(public_poems),
        "glossary_terms": len(terms),
        "people": len(people),
        "events": len(events),
        "themes": len(themes),
        "sources": len(sources),
        "search_documents": len(search_documents),
    }
