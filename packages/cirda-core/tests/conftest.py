"""Shared test fixtures."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cirda_core.ports.clock import Clock


class FixedClock:
    """Fixed clock for deterministic tests."""

    def __init__(self, fixed: datetime | None = None) -> None:
        self._fixed = fixed or datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._fixed


@pytest.fixture
def fixed_clock() -> Clock:
    return FixedClock()
