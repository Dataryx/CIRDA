"""Injectable clock protocol."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    """Time source for domain computations."""

    def now(self) -> datetime:
        """Return current timezone-aware datetime."""
        ...


class SystemClock:
    """Production clock using UTC."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
