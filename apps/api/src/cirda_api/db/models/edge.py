"""Edge-related ORM models."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from cirda_api.db.compat import JsonColumn
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.types import UTCDateTime


class Edge(Base):
    __tablename__ = "edges"

    edge_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(128), ForeignKey("entities.entity_id"), index=True)
    target_id: Mapped[str] = mapped_column(String(128), ForeignKey("entities.entity_id"), index=True)
    relation: Mapped[str] = mapped_column(String(32), nullable=False)
    layer: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    necessity: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_observed_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    valid_from: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    valid_to: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    updated_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    channel_evidence: Mapped[list[Any]] = relationship("EdgeChannelEvidence", back_populates="edge", cascade="all, delete-orphan")
    versions: Mapped[list[Any]] = relationship("EdgeVersion", back_populates="edge", cascade="all, delete-orphan")


class EdgeChannelEvidence(Base):
    __tablename__ = "edge_channel_evidence"
    __table_args__ = (UniqueConstraint("edge_id", "channel", name="uq_edge_channel"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    edge_id: Mapped[str] = mapped_column(String(256), ForeignKey("edges.edge_id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    observation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_observed_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)

    edge: Mapped[Any] = relationship("Edge", back_populates="channel_evidence")


class EdgeVersion(Base):
    __tablename__ = "edge_versions"

    version_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    edge_id: Mapped[str] = mapped_column(String(256), ForeignKey("edges.edge_id", ondelete="CASCADE"), index=True)
    layer: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JsonColumn, nullable=False, default=dict)
    valid_from: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    valid_to: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    edge: Mapped[Any] = relationship("Edge", back_populates="versions")
