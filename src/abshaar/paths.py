from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root from an installed or source checkout."""
    return Path(__file__).resolve().parents[2]


def resolve_root(path: str | Path | None = None) -> Path:
    return Path(path).resolve() if path else repo_root()
