"""String similarity for entity resolution."""

from __future__ import annotations

from difflib import SequenceMatcher


def normalized_key(value: str) -> str:
    """Normalize a string for comparison."""
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def similarity(a: str, b: str) -> float:
    """Return similarity score in [0, 1]."""
    if not a or not b:
        return 0.0
    na, nb = normalized_key(a), normalized_key(b)
    if na == nb:
        return 1.0
    return SequenceMatcher(None, na, nb).ratio()
