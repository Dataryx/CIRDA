"""Benchmark run/result ORM models."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, String, Text
from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    config: Mapped[dict[str, Any]] = mapped_column(JsonColumn, nullable=False, default=dict)
    started_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    completed_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    results: Mapped[list[Any]] = relationship("BenchmarkResult", back_populates="run", cascade="all, delete-orphan")


class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"

    result_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("benchmark_runs.run_id", ondelete="CASCADE"), index=True)
    loss: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(32), nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JsonColumn, nullable=False, default=dict)
    data_class: Mapped[str] = mapped_column(String(64), nullable=False, default="synthetic_benchmark")
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    run: Mapped[Any] = relationship("BenchmarkRun", back_populates="results")
