from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from abshaar.jsonl import write_json, write_jsonl


PARSER_VERSION = "punjab_library_gurmukhi_pdf_v1"
HEADING_RE = re.compile(r"^\s*(\d{1,3})\.\s*(.*\S)\s*$")
SOURCE_ID = "source_punjab_library_kafian_2017"
WATERMARK = "www.PunjabLibrary.com"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _trim_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def segment_page_texts(page_texts: Iterable[str]) -> list[dict[str, Any]]:
    """Split numbered poems while preserving source-page boundaries and raw text order."""

    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for page_number, page_text in enumerate(page_texts, start=1):
        for raw_line in page_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            line = raw_line.replace(WATERMARK, "").rstrip()
            match = HEADING_RE.match(line)
            if match:
                if current is not None:
                    current["source_page_end"] = current["_last_content_page"]
                    current["_lines"] = _trim_blank_edges(current["_lines"])
                    records.append(current)
                ordinal = int(match.group(1))
                title = match.group(2).strip()
                current = {
                    "source_ordinal": ordinal,
                    "title_gurmukhi_extracted": title,
                    "heading_raw": line.strip(),
                    "source_page_start": page_number,
                    "source_page_end": page_number,
                    "_last_content_page": page_number,
                    "_lines": [],
                }
                continue

            if current is not None:
                current["_lines"].append(line)
                if line.strip():
                    current["_last_content_page"] = page_number

    if current is not None:
        current["source_page_end"] = current["_last_content_page"]
        current["_lines"] = _trim_blank_edges(current["_lines"])
        records.append(current)

    normalized: list[dict[str, Any]] = []
    for record in records:
        ordinal = int(record["source_ordinal"])
        normalized.append(
            {
                "id": f"punjab_library_bulleh_shah_kafi_{ordinal:04d}",
                "source_id": SOURCE_ID,
                "source_ordinal": ordinal,
                "title_gurmukhi_extracted": record["title_gurmukhi_extracted"],
                "heading_raw": record["heading_raw"],
                "script": "Gurmukhi",
                "language": "Punjabi",
                "source_page_start": record["source_page_start"],
                "source_page_end": record["source_page_end"],
                "source_text_extracted": "\n".join(record["_lines"]).strip(),
                "extraction": {
                    "method": "pypdf_embedded_text_layer",
                    "parser_version": PARSER_VERSION,
                    "quality_status": "needs_visual_review",
                    "authoritative_representation": "source_pdf_page_image",
                    "known_issues": [
                        "embedded text can omit or misorder Gurmukhi characters",
                        "embedded text contains irregular intra-word spacing",
                        "line and stanza boundaries have not been editorially verified",
                    ],
                },
                "review_status": "needs_review",
            }
        )
    return normalized


def _audit(records: list[dict[str, Any]], expected_count: int | None) -> dict[str, Any]:
    ordinals = [int(record["source_ordinal"]) for record in records]
    unique_ordinals = sorted(set(ordinals))
    upper_bound = expected_count if expected_count is not None else max(unique_ordinals, default=0)
    return {
        "records": len(records),
        "unique_ordinals": len(unique_ordinals),
        "ordinal_min": min(unique_ordinals, default=None),
        "ordinal_max": max(unique_ordinals, default=None),
        "missing_ordinals": [
            number for number in range(1, upper_bound + 1) if number not in set(ordinals)
        ],
        "duplicate_ordinals": sorted(
            number for number in unique_ordinals if ordinals.count(number) > 1
        ),
        "empty_titles": sum(
            1 for record in records if not record["title_gurmukhi_extracted"].strip()
        ),
        "empty_texts": sum(1 for record in records if not record["source_text_extracted"].strip()),
        "extracted_characters": sum(len(record["source_text_extracted"]) for record in records),
    }


def _extract_pages(pdf_path: Path) -> tuple[list[str], str]:
    try:
        import pypdf
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "Gurmukhi PDF extraction requires pypdf. Install the project PDF extra "
            "with `python3 -m pip install -e '.[pdf]'`."
        ) from exc

    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return pages, pypdf.__version__


def extract_gurmukhi_pdf(
    *,
    root: Path,
    pdf_path: Path,
    output_path: Path,
    catalog_output_path: Path,
    run_output_path: Path,
    expected_count: int | None = 160,
) -> dict[str, Any]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    page_texts, pypdf_version = _extract_pages(pdf_path)
    records = segment_page_texts(page_texts)
    audit = _audit(records, expected_count)
    if audit["duplicate_ordinals"] or audit["missing_ordinals"]:
        raise ValueError(
            "Numbered-work audit failed: "
            f"missing={audit['missing_ordinals']} duplicate={audit['duplicate_ordinals']}"
        )
    if expected_count is not None and audit["records"] != expected_count:
        raise ValueError(f"Expected {expected_count} records, extracted {audit['records']}")

    source_sha256 = _sha256(pdf_path)
    for record in records:
        record["source_file"] = {
            "name": pdf_path.name,
            "sha256": source_sha256,
        }

    catalog_records = [
        {
            "id": record["id"],
            "source_id": record["source_id"],
            "source_ordinal": record["source_ordinal"],
            "title_gurmukhi_extracted": record["title_gurmukhi_extracted"],
            "script": record["script"],
            "language": record["language"],
            "source_page_start": record["source_page_start"],
            "source_page_end": record["source_page_end"],
            "witness_record_id": record["id"],
            "review_status": record["review_status"],
            "notes": (
                "Catalog metadata derived from the PDF embedded text layer; title spelling "
                "must be checked against the rendered source page before canonical use."
            ),
        }
        for record in records
    ]

    try:
        source_path = str(pdf_path.relative_to(root))
    except ValueError:
        source_path = str(pdf_path)

    run_record = {
        "id": "run_punjab_library_gurmukhi_pdf",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "parser_version": PARSER_VERSION,
        "pypdf_version": pypdf_version,
        "source_id": SOURCE_ID,
        "source_path": source_path,
        "source_sha256": source_sha256,
        "pdf_pages": len(page_texts),
        "output_path": (
            str(output_path.relative_to(root))
            if output_path.is_relative_to(root)
            else str(output_path)
        ),
        "catalog_output_path": (
            str(catalog_output_path.relative_to(root))
            if catalog_output_path.is_relative_to(root)
            else str(catalog_output_path)
        ),
        "audit": audit,
        "rights_note": (
            "Underlying Bulleh Shah poems are public domain. Rights in this 2017 digital "
            "transcription/edition are not established; full extracted text remains private "
            "and ignored pending verification."
        ),
    }

    write_jsonl(output_path, records)
    write_jsonl(catalog_output_path, catalog_records)
    write_json(run_output_path, run_record)
    return run_record
