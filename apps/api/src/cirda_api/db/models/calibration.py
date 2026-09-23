"""Calibration profile ORM model."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class CalibrationProfile(Base):
    __tablename__ = "calibration_profiles"

    profile_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="default")
    theta_c: Mapped[float] = mapped_column(Float, nullable=False)
    theta_p: Mapped[float] = mapped_column(Float, nullable=False)
    c_min: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    updated_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
