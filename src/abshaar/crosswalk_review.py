"""First-pass classification support for the Sufinama crosswalk review.

The matcher's `score` is a MAX over line-pair similarities, so one shared
refrain or a similar title can score 0.6-0.9 between poems that are otherwise
different works. Classification therefore needs bidirectional line COVERAGE:
what fraction of witness lines have a counterpart in the entry, and vice
versa. This module keeps two halves deliberately separate:

- ``build_crosswalk_evidence``: mechanical, deterministic coverage evidence
  and line alignments for every match record. No judgment; read-only.
- ``apply_crosswalk_classifications``: applies an explicit classifications
  JSONL (one decision per match record, authored by a reviewer — AI first
  pass or human) onto the match files, refusing anything malformed,
  incomplete, or outside the taxonomy.

Decisions live in ``data/annotations/crosswalk_classifications.jsonl`` so a
human can inspect, edit a line, and re-apply. Devanagari-channel similarities
run through the approximate transliteration and are indicative only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from abshaar.devanagari import transliterate_devanagari
from abshaar.jsonl import read_jsonl, write_jsonl
from abshaar.source_matching import (
    _entry_candidates,
    _lines,
    _similarity,
    normalize_arabic,
    normalize_roman,
)

MATCH_STATUSES = ("exact_witness", "variant", "excerpt", "possible", "unmatched")

STRONG_THRESHOLD = 0.80
LOOSE_THRESHOLD = 0.60
# The rule-based Devanagari transliteration (no schwa deletion) depresses
# genuine matches; use a softer loose threshold on that channel so real
# candidates are not triaged straight to "unmatched".
DEVANAGARI_LOOSE_THRESHOLD = 0.55

CORPORA = (
    (
        "kaafi",
        Path("data/context/source_matches.jsonl"),
        Path("data/processed/private/sufinama_match_manifest.jsonl"),
    ),
    (
        "non-kaafi",
        Path("data/context/sufinama_text_source_matches.jsonl"),
        Path("data/processed/private/sufinama_texts_match_manifest.jsonl"),
    ),
)

EVIDENCE_OUTPUT = Path("data/annotations/crosswalk_evidence.md")
CLASSIFICATIONS_PATH = Path("data/annotations/crosswalk_classifications.jsonl")


def _witness_channels(item: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Per-script witness lines as (raw, normalized) pairs; empty keys dropped."""
    channels: dict[str, list[dict[str, str]]] = {}
    for channel, field, normalizer in (
        ("roman", "roman_text", normalize_roman),
        ("urdu", "urdu_text", normalize_arabic),
    ):
        pairs = [
            {"raw": line, "key": normalizer(line)}
            for line in _lines(item.get(field))
        ]
        pairs = [pair for pair in pairs if pair["key"]]
        if pairs:
            channels[channel] = pairs
    devanagari_pairs = []
    for line in _lines(item.get("devanagari_text")):
        key = normalize_roman(transliterate_devanagari(line))
        if key:
            devanagari_pairs.append({"raw": line, "key": key})
    if devanagari_pairs:
        channels["devanagari"] = devanagari_pairs
    return channels


def _entry_channels(candidate: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    roman = [
        {"raw": line, "key": normalize_roman(line)}
        for line in candidate["roman_lines"]
    ]
    roman = [pair for pair in roman if pair["key"]]
    urdu = [
        {"raw": line, "key": normalize_arabic(line)}
        for line in candidate["urdu_lines"]
    ]
    urdu = [pair for pair in urdu if pair["key"]]
    channels: dict[str, list[dict[str, str]]] = {}
    if roman:
        channels["roman"] = roman
        # Approximate Devanagari transliteration compares against roman lines.
        channels["devanagari"] = roman
    if urdu:
        channels["urdu"] = urdu
    return channels


def _alignment(
    source: list[dict[str, str]], target: list[dict[str, str]]
) -> list[dict[str, Any]]:
    """For each source line: the best-matching target line and its similarity."""
    rows = []
    for pair in source:
        best_score = 0.0
        best_raw = ""
        for other in target:
            score = _similarity(pair["key"], other["key"])
            if score > best_score:
                best_score = score
                best_raw = other["raw"]
        rows.append({"raw": pair["raw"], "best": best_raw, "score": round(best_score, 2)})
    return rows


def _coverage(rows: list[dict[str, Any]], threshold: float) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row["score"] >= threshold) / len(rows)


def _channel_evidence(
    witness: list[dict[str, str]], entry: list[dict[str, str]], channel: str
) -> dict[str, Any]:
    forward = _alignment(witness, entry)
    backward = _alignment(entry, witness)
    loose = DEVANAGARI_LOOSE_THRESHOLD if channel == "devanagari" else LOOSE_THRESHOLD
    exact = len({pair["key"] for pair in witness} & {pair["key"] for pair in entry})
    return {
        "channel": channel,
        "witness_lines": len(witness),
        "entry_lines": len(entry),
        "exact_line_matches": exact,
        "witness_coverage_strong": round(_coverage(forward, STRONG_THRESHOLD), 2),
        "entry_coverage_strong": round(_coverage(backward, STRONG_THRESHOLD), 2),
        "witness_coverage_loose": round(_coverage(forward, loose), 2),
        "entry_coverage_loose": round(_coverage(backward, loose), 2),
        "forward": forward,
        "backward": backward,
    }


def _best_channel(channels: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not channels:
        return None
    return max(
        channels,
        key=lambda ch: (
            ch["witness_coverage_strong"] + ch["entry_coverage_strong"],
            ch["witness_coverage_loose"] + ch["entry_coverage_loose"],
        ),
    )


def _proposal(best: dict[str, Any] | None) -> str:
    """Mechanical hint only; the classifications file carries the decision."""
    if best is None:
        return "unmatched"
    w_strong = best["witness_coverage_strong"]
    e_strong = best["entry_coverage_strong"]
    w_loose = best["witness_coverage_loose"]
    e_loose = best["entry_coverage_loose"]
    if w_loose == 0 and e_loose == 0 and best["exact_line_matches"] == 0:
        return "unmatched"
    if w_strong >= 0.9 and e_strong >= 0.9:
        return "exact_witness"
    if w_loose >= 0.7 and e_loose >= 0.7:
        return "variant"
    if (w_loose >= 0.8 and e_loose < 0.5) or (e_loose >= 0.8 and w_loose < 0.5):
        return "excerpt"
    return "possible"


def build_crosswalk_evidence(root: Path, output_path: Path | None = None) -> Path:
    output = root / (output_path or EVIDENCE_OUTPUT)
    entries = {c["poem_id"]: c for c in _entry_candidates(root)}

    lines = [
        "# Crosswalk Evidence Report",
        "",
        "Generated by `abshaar crosswalk-evidence` — deterministic; regenerate",
        "after any crosswalk rebuild; do not edit by hand.",
        "",
        "Coverage answers what the matcher's max-similarity score cannot: how",
        "much of each text is actually present in the other. `w`/`e` prefixes =",
        "witness/entry side; `strong` = share of lines with a counterpart at",
        "similarity >= 0.80; `loose` >= 0.60 (0.55 on the approximate",
        "Devanagari channel). Proposed statuses are mechanical hints; the",
        "decisions live in `crosswalk_classifications.jsonl`.",
        "",
    ]

    for corpus, match_path, manifest_path in CORPORA:
        matches = read_jsonl(root / match_path)
        items = {record["id"]: record for record in read_jsonl(root / manifest_path)}
        lines.append(f"# Corpus: {corpus} ({len(matches)} records)")
        lines.append("")
        for match in matches:
            item = items.get(match["source_item_id"])
            lines.append(f"## {corpus} — {match['source_item_id']}")
            lines.append("")
            if item is None:
                lines.append("MISSING from match manifest — rebuild it first.")
                lines.append("")
                continue
            title_bits = []
            for label, field in (("roman", "roman_title"), ("urdu", "urdu_title"), ("devanagari", "devanagari_title")):
                value = str(item.get(field) or "").strip()
                if value:
                    title_bits.append(f"{label} title: {value}")
            lines.append(f"- {match.get('source_url')}")
            if title_bits:
                lines.append("- " + " | ".join(title_bits))
            witness_channels = _witness_channels(item)

            candidates = match.get("candidate_poems") or []
            record_best: dict[str, Any] | None = None
            record_best_poem = ""
            per_candidate = []
            for candidate_ref in candidates:
                poem_id = candidate_ref["poem_id"]
                entry = entries.get(poem_id)
                if entry is None:
                    per_candidate.append((poem_id, candidate_ref, None, []))
                    continue
                entry_channels = _entry_channels(entry)
                channel_rows = [
                    _channel_evidence(witness_channels[channel], entry_channels[channel], channel)
                    for channel in ("roman", "urdu", "devanagari")
                    if channel in witness_channels and channel in entry_channels
                ]
                best = _best_channel(channel_rows)
                per_candidate.append((poem_id, candidate_ref, best, channel_rows))
                if best is not None and (
                    record_best is None
                    or best["witness_coverage_loose"] + best["entry_coverage_loose"]
                    > record_best["witness_coverage_loose"] + record_best["entry_coverage_loose"]
                ):
                    record_best = best
                    record_best_poem = poem_id

            proposal = _proposal(record_best)
            lines.append(
                f"- proposed: **{proposal}**"
                + (f" (vs {record_best_poem})" if record_best_poem else "")
            )
            lines.append("")

            for poem_id, candidate_ref, best, channel_rows in per_candidate:
                if best is None:
                    lines.append(f"### vs {poem_id} — no comparable channel")
                    lines.append("")
                    continue
                title = entries[poem_id]["title"]
                lines.append(f"### vs {poem_id} ({title}) — matcher score {candidate_ref.get('score')}")
                lines.append("")
                lines.append(
                    "| channel | wit lines | ent lines | exact | w-strong | e-strong | w-loose | e-loose |"
                )
                lines.append("|---|---|---|---|---|---|---|---|")
                for row in channel_rows:
                    lines.append(
                        f"| {row['channel']} | {row['witness_lines']} | {row['entry_lines']} "
                        f"| {row['exact_line_matches']} | {row['witness_coverage_strong']} "
                        f"| {row['entry_coverage_strong']} | {row['witness_coverage_loose']} "
                        f"| {row['entry_coverage_loose']} |"
                    )
                lines.append("")
                show_alignment = (
                    best["witness_coverage_loose"] > 0
                    or best["entry_coverage_loose"] > 0
                    or best["exact_line_matches"] > 0
                    or any(row["score"] >= 0.5 for row in best["forward"])
                )
                if show_alignment:
                    lines.append(f"Alignment ({best['channel']} channel), witness → entry:")
                    lines.append("")
                    lines.append("| witness line | best entry line | sim |")
                    lines.append("|---|---|---|")
                    for row in best["forward"]:
                        lines.append(f"| {row['raw']} | {row['best']} | {row['score']} |")
                    uncovered = [row for row in best["backward"] if row["score"] < 0.6]
                    if uncovered:
                        lines.append("")
                        lines.append("Entry lines with no witness counterpart (sim < 0.6):")
                        lines.append("")
                        for row in uncovered:
                            lines.append(f"- {row['raw']} ({row['score']})")
                    lines.append("")
    text = "\n".join(lines) + "\n"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return output


def apply_crosswalk_classifications(
    root: Path, classifications_path: Path | None = None
) -> dict[str, int]:
    """Apply the classifications file onto both match JSONLs.

    Fails loudly (ValueError) on: unknown/duplicate/missing match ids, a
    status outside the taxonomy, a poem_id that is not among the record's
    stored candidates, unmatched with a poem_id, a non-unmatched status
    without one, or a missing/empty note. Idempotent: re-applying the same
    file reproduces the same bytes.
    """
    path = root / (classifications_path or CLASSIFICATIONS_PATH)
    classifications = read_jsonl(path)
    by_id: dict[str, dict[str, Any]] = {}
    for record in classifications:
        match_id = str(record.get("match_id") or "")
        if not match_id:
            raise ValueError(f"{path}: every classification needs a match_id")
        if match_id in by_id:
            raise ValueError(f"{path}: duplicate classification for {match_id}")
        status = record.get("status")
        if status not in MATCH_STATUSES:
            raise ValueError(
                f"{path}: {match_id}: status {status!r} not in {MATCH_STATUSES}"
            )
        note = str(record.get("note") or "").strip()
        if not note:
            raise ValueError(f"{path}: {match_id}: a non-empty note is required")
        poem_id = record.get("poem_id")
        if status == "unmatched" and poem_id:
            raise ValueError(
                f"{path}: {match_id}: unmatched must not carry a poem_id"
            )
        if status != "unmatched" and not poem_id:
            raise ValueError(f"{path}: {match_id}: status {status} needs a poem_id")
        by_id[match_id] = record

    # Validate everything against both match files BEFORE writing anything,
    # so a bad classifications file can never leave a partial application.
    counts = {status: 0 for status in MATCH_STATUSES}
    seen: set[str] = set()
    updated: list[tuple[Path, list[dict[str, Any]]]] = []
    for corpus, match_path, _ in CORPORA:
        full_path = root / match_path
        matches = read_jsonl(full_path)
        for match in matches:
            match_id = str(match["id"])
            classification = by_id.get(match_id)
            if classification is None:
                raise ValueError(
                    f"{full_path}: {match_id} has no classification in {path}"
                )
            seen.add(match_id)
            poem_id = classification.get("poem_id")
            if poem_id:
                candidate_ids = {
                    candidate["poem_id"]
                    for candidate in match.get("candidate_poems") or []
                }
                if poem_id not in candidate_ids:
                    raise ValueError(
                        f"{path}: {match_id}: poem_id {poem_id} is not among the "
                        f"record's stored candidates {sorted(candidate_ids)}"
                    )
            match["match_status"] = classification["status"]
            match["match_review"] = {
                "poem_id": poem_id,
                "note": classification["note"],
                "method": classification.get("method") or "line_coverage_first_pass",
                "classified_by": classification.get("classified_by") or "unknown",
                "classified_on": classification.get("classified_on") or "unknown",
                "human_confirmed": bool(classification.get("human_confirmed", False)),
            }
            counts[classification["status"]] += 1
        updated.append((full_path, matches))

    unused = sorted(set(by_id) - seen)
    if unused:
        raise ValueError(f"{path}: classifications for unknown match ids: {unused}")

    for full_path, matches in updated:
        write_jsonl(full_path, matches)
    return counts
