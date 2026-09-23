"""Entity alias ORM model."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class Alias(Base):
    __tablename__ = "aliases"
    __table_args__ = (UniqueConstraint("entity_id", "alias", name="uq_alias_entity_alias"),)

    alias_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(128), ForeignKey("entities.entity_id", ondelete="CASCADE"), index=True)
    alias: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    entity: Mapped[Any] = relationship("Entity", back_populates="aliases")
