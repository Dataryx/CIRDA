"""Coverage snapshot ORM model."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, Integer, String
from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class CoverageSnapshot(Base):
    __tablename__ = "coverage_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    coverage: Mapped[float] = mapped_column(Float, nullable=False)
    observed_entities: Mapped[int] = mapped_column(Integer, nullable=False)
    total_entities: Mapped[int] = mapped_column(Integer, nullable=False)
    suppressed_channels: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False, default=list)
    scope: Mapped[str | None] = mapped_column(String(128), nullable=True)
    captured_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False, index=True)
