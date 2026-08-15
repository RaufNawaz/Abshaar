from __future__ import annotations

import re
import unicodedata


# Square brackets are also legitimate corpus conventions (uncertainty notes like
# "[uncertain line — …]", supplied words, [[cross-references]]), so a blanket
# \[.+\] match produces false positives on finished entries. Only the known
# template slots and instruction-verb brackets below count as placeholders.
_PLACEHOLDER_PATTERNS = [
    r"\[first line or working title\]",
    r"\[paste or type[^\]]*\]",
    r"\[type latin transliteration[^\]]*\]",
    r"\[reference translation, e\.g\.[^\]]*\]",
    r"\[ai-drafted english translation[^\]]*\]",
    r"\[your own literary translation\.?\]",
    r"\[explanation of metaphor[^\]]*\]",
    r"\[human-reviewed answer[^\]]*\]",
    r"\[clearly labeled ai translation[^\]]*\]",
    r"\[literal gloss here\]",
    r"\[project literary translation here\]",
    r"\[model name\]",
    r"\[prompt version\]",
    r"\[(?:explain|add|describe|fill in|insert|write|paste|todo)\b[^\]]*\]",
    r"yes/no/unknown",
    r"public-domain/permission-cleared",
]
PLACEHOLDER_RE = re.compile("|".join(_PLACEHOLDER_PATTERNS), re.I)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.lower()
    ascii_value = re.sub(r"[^a-z0-9]+", "_", ascii_value)
    return ascii_value.strip("_") or "untitled"


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def has_placeholder(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(PLACEHOLDER_RE.search(value))
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def nonempty_lines(value: str) -> list[str]:
    return [line.rstrip() for line in value.splitlines() if line.strip()]
