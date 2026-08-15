from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from abshaar.devanagari import transliterate_devanagari
from abshaar.jsonl import read_jsonl, write_jsonl
from abshaar.markdown_entry import parse_markdown_entry
from abshaar.validation import iter_working_entries


# Devanagari comparison runs through an APPROXIMATE transliteration, so a
# similarity derived from it must never reach 1.0: exact-score candidates are
# auto-merged into canonical work clusters, and approximate evidence must not
# trigger that.
DEVANAGARI_SCORE_CAP = 0.98


ARABIC_CHAR_EQUIVALENTS = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ہ",
        "ة": "ہ",
        "آ": "ا",
        "أ": "ا",
        "إ": "ا",
        "ؤ": "و",
        "ئ": "ی",
    }
)


def _without_marks(value: str) -> str:
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )


def normalize_roman(value: str) -> str:
    value = _without_marks(value).casefold()
    return "".join(character for character in value if character.isalnum())


def normalize_arabic(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).translate(ARABIC_CHAR_EQUIVALENTS)
    value = value.replace("ـ", "")
    return "".join(
        character
        for character in value
        if unicodedata.category(character)[0] not in {"M", "P", "C", "Z"}
    )


def _first_line(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return next((line.strip() for line in value.splitlines() if line.strip()), "")


def _lines(value: object) -> list[str]:
    if not isinstance(value, str):
        return []
    return [line.strip() for line in value.splitlines() if line.strip()]


def _similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    return SequenceMatcher(None, left, right).ratio()


def _entry_candidates(root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in iter_working_entries(root):
        entry = parse_markdown_entry(path)
        candidates.append(
            {
                "poem_id": str(entry.front_matter.get("id") or path.stem),
                "title": str(entry.front_matter.get("title") or ""),
                "roman_lines": _lines(entry.sections.get("transliteration", "")),
                "urdu_lines": _lines(entry.sections.get("original", "")),
            }
        )
    return candidates


def _best_line_similarity(left: list[str], right: list[str]) -> float:
    return max((_similarity(a, b) for a in left for b in right), default=0.0)


def _exact_line_matches(left: list[str], right: list[str]) -> int:
    return len(set(left) & set(right))


def _score_item(item: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    roman_title = normalize_roman(
        str(item.get("roman_title") or item.get("title_roman") or "")
    )
    roman_source_lines = [normalize_roman(line) for line in _lines(item.get("roman_text"))]
    roman_source_lines = [line for line in roman_source_lines if line]
    urdu_title = normalize_arabic(
        str(item.get("urdu_title") or item.get("title_urdu") or "")
    )
    urdu_source_lines = [normalize_arabic(line) for line in _lines(item.get("urdu_text"))]
    urdu_source_lines = [line for line in urdu_source_lines if line]

    candidate_title = normalize_roman(candidate["title"])
    candidate_roman_lines = [normalize_roman(line) for line in candidate["roman_lines"]]
    candidate_roman_lines = [line for line in candidate_roman_lines if line]
    candidate_urdu_lines = [normalize_arabic(line) for line in candidate["urdu_lines"]]
    candidate_urdu_lines = [line for line in candidate_urdu_lines if line]

    title_targets = [candidate_title, *candidate_roman_lines]
    roman_exact = _exact_line_matches(roman_source_lines, candidate_roman_lines)
    urdu_exact = _exact_line_matches(urdu_source_lines, candidate_urdu_lines)

    devanagari_title = normalize_roman(
        transliterate_devanagari(str(item.get("devanagari_title") or ""))
    )
    devanagari_lines = [
        normalize_roman(transliterate_devanagari(line))
        for line in _lines(item.get("devanagari_text"))
    ]
    devanagari_lines = [line for line in devanagari_lines if line]

    signals = {
        "roman_title_to_title": _similarity(roman_title, candidate_title),
        "roman_title_to_any_line": _best_line_similarity([roman_title], title_targets),
        "roman_any_line": _best_line_similarity(roman_source_lines, candidate_roman_lines),
        "urdu_title_to_any_line": _best_line_similarity([urdu_title], candidate_urdu_lines),
        "urdu_any_line": _best_line_similarity(urdu_source_lines, candidate_urdu_lines),
    }
    devanagari_signals = {
        "devanagari_title_to_any_line": _best_line_similarity([devanagari_title], title_targets)
        if devanagari_title
        else 0.0,
        "devanagari_any_line": _best_line_similarity(devanagari_lines, candidate_roman_lines),
    }
    best_roman = max(signals["roman_title_to_any_line"], signals["roman_any_line"])
    best_urdu = max(signals["urdu_title_to_any_line"], signals["urdu_any_line"])
    score = max(signals.values(), default=0.0)
    if best_roman >= 0.75 and best_urdu >= 0.75:
        score = max(score, min(1.0, (best_roman + best_urdu) / 2 + 0.05))
    score = max(score, min(DEVANAGARI_SCORE_CAP, max(devanagari_signals.values(), default=0.0)))
    signals.update(devanagari_signals)
    if roman_exact or urdu_exact:
        score = 1.0
    nonzero = {key: round(value, 4) for key, value in signals.items() if value > 0}
    return {
        "poem_id": candidate["poem_id"],
        "score": round(score, 4),
        "exact_line_matches": {"roman": roman_exact, "urdu": urdu_exact},
        "signals": nonzero,
    }


def match_source_manifest(
    root: Path,
    manifest_path: Path,
    output_path: Path,
    top_n: int = 3,
) -> list[dict[str, Any]]:
    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    items = read_jsonl(manifest_path)
    candidates = _entry_candidates(root)
    matches: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for item in items:
        source_item_id = str(item.get("id") or item.get("source_item_id") or "").strip()
        if not source_item_id:
            raise ValueError(f"{manifest_path}: every source item needs an `id`")
        if source_item_id in seen_ids:
            raise ValueError(f"{manifest_path}: duplicate source item id `{source_item_id}`")
        seen_ids.add(source_item_id)

        ranked = [_score_item(item, candidate) for candidate in candidates]
        ranked.sort(key=lambda value: (-float(value["score"]), str(value["poem_id"])))
        candidate_poems = [value for value in ranked[:top_n] if value["score"] > 0]

        matches.append(
            {
                "id": f"source_match_{source_item_id}",
                "source_item_id": source_item_id,
                "source_id": item.get("source_id"),
                "source_url": item.get("url") or item.get("url_roman"),
                "source_url_urdu": item.get("url_urdu"),
                "candidate_poems": candidate_poems,
                "match_status": "needs_review",
                "notes": (
                    "Candidate match only. Review source/version differences and link the "
                    "source witness without overwriting or collapsing canonical poem text."
                ),
            }
        )

    write_jsonl(output_path, matches)
    return matches
