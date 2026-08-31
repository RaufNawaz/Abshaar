from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from abshaar.text import nonempty_lines, slugify, strip_quotes


# The `# Literal Translation` slot in Rafat entries holds Taufiq Rafat's
# copyrighted published rendering, identified by its citation note. It must
# serialize as `reference_translation` with trainable=False, never as a
# project literal gloss.
REFERENCE_ATTRIBUTION_RE = re.compile(r"reference translation by|taufiq rafat", re.I)
AI_DRAFT_ATTRIBUTION_RE = re.compile(r"ai-drafted", re.I)


def _attribution(text: str) -> tuple[str, str | None]:
    if AI_DRAFT_ATTRIBUTION_RE.search(text):
        return "ai", "claude"
    return "human", None


SECTION_ALIASES = {
    "original": "original",
    "script notes": "script_notes",
    "transliteration": "transliteration",
    "literal gloss": "literal_gloss",
    "literal translation": "literal_gloss",
    # Added 2026-08-31. `# Literal Translation` in the Rafat entries holds a
    # published third-party rendering, so the slot named for a literal gloss
    # contained neither a gloss nor the project's own work. New entries should
    # use `# Reference Translation` for third-party text and keep
    # `# Literal Translation` for the project's own close rendering; the
    # attribution heuristic below stays as a fallback for unmigrated entries.
    "reference translation": "reference_translation",
    "ai translation": "ai_translation",
    "literary translation": "literary_translation",
    "tashreeh": "tashreeh",
    "key terms": "key_terms",
    "themes": "themes",
    "source notes": "source_notes",
    "review notes": "review_notes",
}


@dataclass(frozen=True)
class MarkdownEntry:
    path: Path
    front_matter: dict[str, Any]
    sections: dict[str, str]


def parse_front_matter(lines: list[str]) -> tuple[dict[str, Any], list[str]]:
    if not lines or lines[0].strip() != "---":
        return {}, lines

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise ValueError("front matter starts with --- but never closes")

    raw = lines[1:end_index]
    parsed: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in raw:
        if not raw_line.strip():
            continue
        stripped = raw_line.strip()
        if stripped.startswith("- ") and current_key:
            parsed.setdefault(current_key, [])
            if not isinstance(parsed[current_key], list):
                parsed[current_key] = [parsed[current_key]]
            parsed[current_key].append(strip_quotes(stripped[2:].strip()))
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        current_key = key.strip()
        value = strip_quotes(value.strip())
        parsed[current_key] = [] if value == "" else value

    return parsed, lines[end_index + 1 :]


def parse_sections(lines: list[str]) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip().lower()
            current = SECTION_ALIASES.get(title, slugify(title))
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)

    return {key: "\n".join(value).strip() for key, value in sections.items()}


def parse_markdown_entry(path: Path) -> MarkdownEntry:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    front_matter, body_lines = parse_front_matter(lines)
    return MarkdownEntry(path=path, front_matter=front_matter, sections=parse_sections(body_lines))


def parse_bullet_map(section_text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()
        if ":" in item:
            key, value = item.split(":", 1)
            values[key.strip().lower()] = value.strip()
        elif "? " in item:
            key, value = item.split("?", 1)
            values[f"{key.strip().lower()}?"] = value.strip()
        else:
            values[item.strip().lower()] = ""
    return values


def parse_bullet_values(section_text: str) -> list[str]:
    values: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        item = stripped[2:].strip()
        if ":" in item:
            item = item.split(":", 1)[0].strip()
        if item:
            values.append(item)
    return values


def _reference_slot_records(poem_id: str, text: str, review_status: str) -> list[dict[str, Any]]:
    """An explicit `# Reference Translation` section, when the entry has one.

    Third-party published text: never publishable, and trainable only when a
    caller deliberately opens the rights gate (see training_export).
    """
    if not text.strip():
        return []
    return [
        {
            "id": f"trans_{poem_id}_reference",
            "kind": "reference_translation",
            "text": text,
            "created_by": "human",
            "model": None,
            "prompt_version": None,
            "status": review_status,
            "rights": "copyrighted",
            "publishable": False,
            "trainable": False,
        }
    ]


def _literal_slot_record(poem_id: str, text: str, review_status: str) -> list[dict[str, Any]]:
    """The `# Literal Translation` slot, empty in entries migrated to the
    explicit reference section. An empty slot emits nothing rather than a
    placeholder record."""
    if not text.strip():
        return []
    if REFERENCE_ATTRIBUTION_RE.search(text):
        return [{
            "id": f"trans_{poem_id}_reference",
            "kind": "reference_translation",
            "text": text,
            "created_by": "human",
            "model": None,
            "prompt_version": None,
            "status": review_status,
            "rights": "copyrighted",
            "publishable": False,
            "trainable": False,
        }]
    created_by, model = _attribution(text)
    return [{
        "id": f"trans_{poem_id}_literal",
        "kind": "literal_gloss",
        "text": text,
        "created_by": created_by,
        "model": model,
        "prompt_version": None,
        "status": review_status,
        "rights": "project",
        "trainable": True,
    }]


def entry_to_poem_record(entry: MarkdownEntry) -> dict[str, Any]:
    fm = entry.front_matter
    sections = entry.sections
    poem_id = str(fm.get("id") or slugify(entry.path.stem))
    poet_id = str(fm.get("poet_id") or "unknown_poet")
    source_ids = fm.get("source_ids") or []
    if isinstance(source_ids, str):
        source_ids = [source_ids]

    script_notes = parse_bullet_map(sections.get("script_notes", ""))
    source_notes = parse_bullet_map(sections.get("source_notes", ""))

    script = script_notes.get("script") or "unknown"
    language_note = script_notes.get("language spans") or "unknown"
    primary_language = language_note.split("/")[0].split(",")[0].strip() or "unknown"

    original_text = sections.get("original", "")
    transliteration_text = sections.get("transliteration", "")
    literal_gloss = sections.get("literal_gloss", "")
    reference_translation = sections.get("reference_translation", "")
    ai_translation = sections.get("ai_translation", "")
    literary_translation = sections.get("literary_translation", "")
    tashreeh = sections.get("tashreeh", "")

    original_lines = nonempty_lines(original_text)
    segmentation = [
        {
            "segment_id": f"{poem_id}_l{index}",
            "text": line,
            "role": "line",
            "notes": "",
        }
        for index, line in enumerate(original_lines, start=1)
    ]

    raw_terms = parse_bullet_values(sections.get("key_terms", ""))
    glossary_terms = [
        term if term.startswith("term_") else f"term_{slugify(term)}_{poet_id}"
        for term in raw_terms
        if term and not term.startswith("[")
    ]

    raw_themes = parse_bullet_values(sections.get("themes", ""))
    themes = [
        theme if theme.startswith("theme_") else f"theme_{slugify(theme)}"
        for theme in raw_themes
        if theme and not theme.startswith("[")
    ]

    can_publish = source_notes.get("can this be published?", "").lower() == "yes"
    review_status = str(fm.get("review_status") or "draft")
    rights_status = str(fm.get("rights_status") or source_notes.get("rights status") or "unknown")

    return {
        "id": poem_id,
        "poet_id": poet_id,
        "title": str(fm.get("title") or entry.path.stem),
        "work_type": str(fm.get("work_type") or "unknown"),
        "source_ids": source_ids,
        "rights_status": rights_status,
        "original": {
            "text": original_text,
            "script": script,
            "language_spans": [
                {
                    "text": original_text,
                    "language": primary_language,
                    "confidence": 0.0,
                    "notes": language_note,
                }
            ],
        },
        "transliteration": {
            "scheme": "project-latin-v1",
            "text": transliteration_text,
            "review_status": review_status,
        },
        "segmentation": segmentation,
        "translations": [
            *_reference_slot_records(poem_id, reference_translation, review_status),
            *_literal_slot_record(poem_id, literal_gloss, review_status),
            {
                "id": f"trans_{poem_id}_ai",
                "kind": "ai_translation",
                "text": ai_translation,
                "created_by": "ai",
                "model": "claude",
                "prompt_version": None,
                "status": review_status,
                "rights": "project",
                "trainable": True,
            },
            {
                "id": f"trans_{poem_id}_literary",
                "kind": "literary_translation",
                "text": literary_translation,
                "created_by": _attribution(literary_translation)[0],
                "model": _attribution(literary_translation)[1],
                "prompt_version": None,
                "status": review_status,
                "rights": "project",
                "trainable": True,
            },
        ],
        "tashreeh": [
            {
                "id": f"tash_{poem_id}_beginner",
                "audience": "beginner",
                "text": tashreeh,
                "created_by": _attribution(tashreeh)[0],
                "model": _attribution(tashreeh)[1],
                "status": review_status,
                "rights": "project",
                "trainable": True,
            }
        ],
        "glossary_terms": glossary_terms,
        "themes": themes,
        "related_poems": [],
        "review": {
            "status": review_status,
            "reviewer": None,
            "confidence": None,
            "last_reviewed_at": None,
        },
        "publication": {
            "include_on_website": can_publish and review_status == "publishable",
            "reason_not_public": "" if can_publish else "source and review not finalized",
        },
        "working_entry_path": str(entry.path.as_posix()),
    }
