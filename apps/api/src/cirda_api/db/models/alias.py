"""Entity alias ORM model."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class Alias(Base):
    __tablename__ = "aliases"
    __table_args__ = (
        UniqueConstraint("tenant_id", "entity_id", "alias", name="uq_alias_tenant_entity_alias"),
        ForeignKeyConstraint(
            ["tenant_id", "entity_id"],
            ["entities.tenant_id", "entities.entity_id"],
            ondelete="CASCADE",
            name="fk_aliases_entity",
        ),
    )

    alias_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, default="default", index=True)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    entity: Mapped[Any] = relationship("Entity", back_populates="aliases")
