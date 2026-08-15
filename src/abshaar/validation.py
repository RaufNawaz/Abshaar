from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl
from abshaar.markdown_entry import entry_to_poem_record, parse_markdown_entry
from abshaar.text import has_placeholder


@dataclass(frozen=True)
class Issue:
    level: str
    location: str
    message: str

    def format(self) -> str:
        return f"{self.level.upper()}: {self.location}: {self.message}"


REQUIRED_POEM_FIELDS = [
    "id",
    "poet_id",
    "title",
    "work_type",
    "source_ids",
    "rights_status",
    "original",
    "transliteration",
    "translations",
    "tashreeh",
    "review",
    "publication",
]


def validate_poem_record(record: dict[str, Any], location: str) -> list[Issue]:
    issues: list[Issue] = []

    for field in REQUIRED_POEM_FIELDS:
        if field not in record:
            issues.append(Issue("error", location, f"missing required field `{field}`"))

    poem_id = record.get("id", "<unknown>")
    original = record.get("original") or {}
    if not isinstance(original, dict) or not str(original.get("text", "")).strip():
        issues.append(Issue("warning", location, f"{poem_id}: original text is empty"))

    transliteration = record.get("transliteration") or {}
    if not isinstance(transliteration, dict) or not str(transliteration.get("text", "")).strip():
        issues.append(Issue("warning", location, f"{poem_id}: transliteration is empty"))

    translations = record.get("translations") or []
    if not isinstance(translations, list) or len(translations) < 2:
        issues.append(Issue("warning", location, f"{poem_id}: expected literal and literary translations"))
    else:
        kinds = {item.get("kind") for item in translations if isinstance(item, dict)}
        if not kinds & {"literal_gloss", "reference_translation"}:
            issues.append(
                Issue(
                    "warning",
                    location,
                    f"{poem_id}: missing literal_gloss or reference_translation",
                )
            )
        if "literary_translation" not in kinds:
            issues.append(Issue("warning", location, f"{poem_id}: missing literary_translation"))
        for item in translations:
            if not isinstance(item, dict):
                continue
            if item.get("kind") == "reference_translation" and item.get("trainable") is not False:
                issues.append(
                    Issue(
                        "error",
                        location,
                        f"{poem_id}: reference_translation must have trainable=false",
                    )
                )

    if has_placeholder(record):
        issues.append(Issue("warning", location, f"{poem_id}: placeholder text remains"))

    publication = record.get("publication") or {}
    if publication.get("include_on_website") and record.get("rights_status") not in {
        "public-domain",
        "permission-cleared",
        "project-original",
    }:
        issues.append(
            Issue(
                "error",
                location,
                f"{poem_id}: publishable record has unsafe rights_status `{record.get('rights_status')}`",
            )
        )

    return issues


def iter_working_entries(root: Path) -> list[Path]:
    working_dir = root / "data" / "working"
    if not working_dir.exists():
        return []
    return sorted(
        path
        for path in working_dir.glob("*.md")
        if path.name.lower() != "readme.md" and "template" not in path.stem.lower()
    )


def validate_working_entries(root: Path) -> list[Issue]:
    from abshaar.translit import lint_translit_v1

    issues: list[Issue] = []
    for path in iter_working_entries(root):
        location = str(path.relative_to(root))
        try:
            entry = parse_markdown_entry(path)
            record = entry_to_poem_record(entry)
        except Exception as exc:  # noqa: BLE001 - validation should report all parse failures.
            issues.append(Issue("error", location, f"could not parse entry: {exc}"))
            continue
        issues.extend(validate_poem_record(record, location))
        transliteration = entry.sections.get("transliteration", "")
        if transliteration and not has_placeholder(transliteration):
            for problem in lint_translit_v1(transliteration):
                issues.append(
                    Issue("warning", location, f"transliteration style: {problem}")
                )
    return issues


def validate_jsonl_file(path: Path, root: Path) -> list[Issue]:
    issues: list[Issue] = []
    location = str(path.relative_to(root))
    try:
        records = read_jsonl(path)
    except ValueError as exc:
        return [Issue("error", location, str(exc))]

    seen_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        record_location = f"{location}:{index}"
        record_id = str(record.get("id") or "")
        if not record_id:
            issues.append(Issue("error", record_location, "record has no `id`"))
        elif record_id in seen_ids:
            issues.append(Issue("error", record_location, f"duplicate id `{record_id}`"))
        seen_ids.add(record_id)

        if path.name == "poems.jsonl":
            issues.extend(validate_poem_record(record, record_location))
        elif has_placeholder(record):
            issues.append(Issue("warning", record_location, "placeholder text remains"))
    return issues


def validate_project(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    issues.extend(validate_working_entries(root))

    candidate_files = [
        root / "data" / "processed" / "poems.jsonl",
        root / "data" / "lexicon" / "terms.jsonl",
        root / "data" / "context" / "sources.jsonl",
        root / "data" / "context" / "people.jsonl",
        root / "data" / "context" / "events.jsonl",
        root / "data" / "context" / "themes.jsonl",
        root / "data" / "context" / "source_matches.jsonl",
        root / "data" / "context" / "sufinama_source_items.jsonl",
        root / "data" / "context" / "sufinama_text_source_items.jsonl",
        root / "data" / "context" / "sufinama_text_source_matches.jsonl",
        root / "data" / "context" / "punjab_library_source_items.jsonl",
        root / "data" / "context" / "biographical_claims.jsonl",
        root / "data" / "context" / "sufinama_bulleh_shah_inventory.jsonl",
        root / "data" / "context" / "canonical_clusters.jsonl",
        root / "data" / "processed" / "training" / "trainable_layers.jsonl",
        root / "data" / "processed" / "private" / "knowledge_base.jsonl",
        root / "data" / "processed" / "private" / "sufinama_bulleh_shah_other_texts.jsonl",
        root / "data" / "annotations" / "reviews.jsonl",
        root / "data" / "annotations" / "model_outputs.jsonl",
    ]
    for path in candidate_files:
        if path.exists():
            issues.extend(validate_jsonl_file(path, root))
    return issues
