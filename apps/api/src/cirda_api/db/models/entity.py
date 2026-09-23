"""Entity ORM model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import String

from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class Entity(Base):
    __tablename__ = "entities"

    entity_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    criticality: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JsonColumn, nullable=False, default=dict)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    updated_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    aliases: Mapped[list[Any]] = relationship("Alias", back_populates="entity", cascade="all, delete-orphan")
