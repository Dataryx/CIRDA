"""Audit log ORM model."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String
from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    principal_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JsonColumn, nullable=False, default=dict)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False, index=True)
