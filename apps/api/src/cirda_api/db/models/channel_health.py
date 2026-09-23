"""Channel health ORM model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class ChannelHealth(Base):
    __tablename__ = "channel_health"

    channel: Mapped[str] = mapped_column(String(32), primary_key=True)
    health_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    lag_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_checked_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    details: Mapped[str | None] = mapped_column(String(512), nullable=True)
