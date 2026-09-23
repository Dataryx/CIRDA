"""Custom SQLAlchemy column types."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """Timezone-aware UTC datetime; rejects naive values."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("naive datetime not allowed")
        return value.astimezone(timezone.utc)

    def process_result_value(self, value: datetime | None, dialect: object) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("naive datetime returned from database")
        return value.astimezone(timezone.utc)

    @staticmethod
    def coerce(value: Any) -> datetime:
        if not isinstance(value, datetime):
            raise TypeError("expected datetime")
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("naive datetime not allowed")
        return value.astimezone(timezone.utc)
