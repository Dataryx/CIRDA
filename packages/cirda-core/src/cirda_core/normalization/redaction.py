"""PII and secret redaction."""

from __future__ import annotations

import re
from typing import Any

_REDACT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+"), r"\1=***"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "***@***"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "***-**-****"),
)


def redact_string(value: str) -> str:
    """Redact sensitive patterns from a string."""
    result = value
    for pattern, replacement in _REDACT_PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def redact_value(value: Any) -> Any:
    """Recursively redact sensitive values."""
    if isinstance(value, str):
        return redact_string(value)
    if isinstance(value, dict):
        return {k: redact_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    if isinstance(value, tuple):
        return tuple(redact_value(v) for v in value)
    return value
