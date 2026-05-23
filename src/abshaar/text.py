from __future__ import annotations

import re
import unicodedata


PLACEHOLDER_RE = re.compile(r"\[[^\]]+\]|yes/no/unknown|public-domain/permission-cleared", re.I)


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
