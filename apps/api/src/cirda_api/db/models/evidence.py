"""Evidence event ORM model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class EvidenceEvent(Base):
    __tablename__ = "evidence_events"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_evidence_idempotency"),)

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    relation: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payload_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    observed_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False, index=True)
    ingested_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
