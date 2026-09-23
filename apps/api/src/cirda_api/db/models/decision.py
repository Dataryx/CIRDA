"""Decision ORM models (immutable records, INV-013)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, String, Text
from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class Decision(Base):
    __tablename__ = "decisions"

    decision_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id: Mapped[str] = mapped_column(String(128), ForeignKey("entities.entity_id"), index=True)
    verdict: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    coverage: Mapped[float] = mapped_column(Float, nullable=False)
    truncated: Mapped[bool] = mapped_column(nullable=False, default=False)
    reason_codes: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False, default=list)
    rationale: Mapped[dict[str, Any]] = mapped_column(JsonColumn, nullable=False, default=dict)
    as_of: Mapped[Any] = mapped_column(UTCDateTime, nullable=False, index=True)
    engine_version: Mapped[str] = mapped_column(String(16), nullable=False)
    change_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supersedes_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("decisions.decision_id"), nullable=True)
    superseded_by_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("decisions.decision_id"), nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)

    paths: Mapped[list[Any]] = relationship("DecisionPath", back_populates="decision", cascade="all, delete-orphan")
    runbook_executions: Mapped[list[Any]] = relationship("RunbookExecution", back_populates="decision", cascade="all, delete-orphan")


class DecisionPath(Base):
    __tablename__ = "decision_paths"

    path_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id: Mapped[str] = mapped_column(String(36), ForeignKey("decisions.decision_id", ondelete="CASCADE"), index=True)
    path_nodes: Mapped[list[str]] = mapped_column(JsonColumn, nullable=False)
    path_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_critical_path: Mapped[bool] = mapped_column(nullable=False, default=False)

    decision: Mapped[Any] = relationship("Decision", back_populates="paths")


class RunbookExecution(Base):
    __tablename__ = "runbook_executions"

    execution_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    decision_id: Mapped[str] = mapped_column(String(36), ForeignKey("decisions.decision_id", ondelete="CASCADE"), index=True)
    stage: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    started_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    completed_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    decision: Mapped[Any] = relationship("Decision", back_populates="runbook_executions")
