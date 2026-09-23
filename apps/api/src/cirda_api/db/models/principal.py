"""Principal (auth subject) ORM model."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, String
from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class Principal(Base):
    __tablename__ = "principals"

    principal_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    subject: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    roles: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False, default=list)
    api_key_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    updated_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
