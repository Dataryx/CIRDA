"""UTCDateTime type tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cirda_api.db.types import UTCDateTime


def test_rejects_naive_datetime() -> None:
    col = UTCDateTime()
    with pytest.raises(ValueError, match="naive"):
        col.process_bind_param(datetime(2024, 1, 1), None)


def test_accepts_aware_datetime() -> None:
    col = UTCDateTime()
    aware = datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert col.process_bind_param(aware, None) == aware
