"""project-latin-v1 transliteration normalizer and linter.

Implements the decisions Rauf recorded in docs/16 §3 on 2026-08-15 (macron
long vowels; dotted retroflexes; nasal inventory n / n̄ / ṇ; ʿain and ġain
symbols; aspiration digraphs; sentence-case line starts, mixed case tolerated;
full Arabic-loan marking as the TARGET, with only already-marked text
standardized mechanically — new loan marks require reading the Urdu and are
review work, never automated).

Scope: the `# Transliteration` section of working entries ONLY. Original,
reference-translation, and interpretive sections are never touched.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from abshaar.validation import iter_working_entries


NASALIZATION = "n̄"  # n + combining macron above, per Rauf's choice

# Order matters: longest sources first so `aa` wins before any `a` handling.
_VOWEL_MAP = [
    ("aa", "ā"), ("Aa", "Ā"), ("AA", "Ā"),
    ("ee", "ī"), ("Ee", "Ī"), ("EE", "Ī"),
    ("oo", "ū"), ("Oo", "Ū"), ("OO", "Ū"),
]

_NASAL_MAP = [("ṅ", NASALIZATION), ("ṁ", NASALIZATION), ("ṉ", NASALIZATION)]

# The letter names ʿain/ġain appear in the letter-mysticism poems marked with
# a plain apostrophe or bare gh; these are the only mechanical ain/ghain fixes.
_AIN_RULES = [
    (re.compile(r"'(?=[Aa]in\b)"), "ʿ"),
    (re.compile(r"'?\bghain\b"), "ġain"),
    (re.compile(r"'?\bGhain\b"), "Ġain"),
]

# Rejected-style markers the linter reports after normalization.
_LINT_PATTERNS = [
    (re.compile(r"aa|ee|oo", re.I), "doubled vowel (use macrons: ā ī ū)"),
    (re.compile(r"[ṅṁṉ]"), f"legacy nasal mark (use {NASALIZATION} for nasalization, ṇ for retroflex)"),
    (re.compile(r"'(?=[Aa]in\b)"), "apostrophe-marked ain (use ʿ)"),
]


def normalize_translit_v1(text: str) -> str:
    for source, target in _VOWEL_MAP:
        text = text.replace(source, target)
    for source, target in _NASAL_MAP:
        text = text.replace(source, target)
    for pattern, replacement in _AIN_RULES:
        text = pattern.sub(replacement, text)
    lines = []
    for line in text.splitlines():
        match = re.search(r"[^\W\d_]", line)
        if match and match.group(0).islower():
            index = match.start()
            line = line[:index] + line[index].upper() + line[index + 1 :]
        lines.append(line)
    return "\n".join(lines)


def lint_translit_v1(text: str) -> list[str]:
    issues = []
    for pattern, message in _LINT_PATTERNS:
        hits = pattern.findall(text)
        if hits:
            issues.append(f"{message} ×{len(hits)}")
    return issues


SECTION_RE = re.compile(r"(?ms)^(# Transliteration\n)(.*?)(?=^# )")


def normalize_entries(root: Path, apply: bool = False) -> dict[str, Any]:
    """Normalize the Transliteration section of every working entry.

    Dry-run by default: returns per-file change counts without writing.
    With apply=True, rewrites only the Transliteration section bytes.
    """
    changed: list[str] = []
    unchanged: list[str] = []
    residual_lint: dict[str, list[str]] = {}

    for path in iter_working_entries(root):
        original_file = path.read_text(encoding="utf-8")
        match = SECTION_RE.search(original_file)
        if not match:
            unchanged.append(path.stem)
            continue
        body = match.group(2)
        # splitlines/join eats trailing blank lines; always restore exactly one
        # blank line between the section body and the next heading.
        normalized = normalize_translit_v1(body.rstrip("\n")) + "\n\n"
        if normalized != body:
            changed.append(path.stem)
            if apply:
                new_file = (
                    original_file[: match.start(2)] + normalized + original_file[match.end(2) :]
                )
                # Path.open, not write_text(newline=...): the latter needs
                # Python >=3.10 and this repo's venv may be 3.9 (see the
                # identical 2026-07-12 sufinama cache bug in OFFLOADING.md).
                with path.open("w", encoding="utf-8", newline="\n") as handle:
                    handle.write(new_file)
        else:
            unchanged.append(path.stem)
        lint = lint_translit_v1(normalized)
        if lint:
            residual_lint[path.stem] = lint

    return {
        "changed": changed,
        "unchanged": unchanged,
        "residual_lint": residual_lint,
        "applied": apply,
    }
