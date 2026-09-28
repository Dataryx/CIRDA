"""Edge-related ORM models."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cirda_api.db.base import Base
from cirda_api.db.compat import JsonColumn
from cirda_api.db.types import UTCDateTime


class Edge(Base):
    __tablename__ = "edges"
    __table_args__ = (
        PrimaryKeyConstraint("tenant_id", "edge_id"),
        ForeignKeyConstraint(
            ["tenant_id", "source_id"],
            ["entities.tenant_id", "entities.entity_id"],
            name="fk_edges_source",
        ),
        ForeignKeyConstraint(
            ["tenant_id", "target_id"],
            ["entities.tenant_id", "entities.entity_id"],
            name="fk_edges_target",
        ),
    )

    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, default="default", index=True)
    edge_id: Mapped[str] = mapped_column(String(256), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
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

    channel_evidence: Mapped[list[Any]] = relationship(
        "EdgeChannelEvidence", back_populates="edge", cascade="all, delete-orphan"
    )
    versions: Mapped[list[Any]] = relationship(
        "EdgeVersion", back_populates="edge", cascade="all, delete-orphan"
    )


class EdgeChannelEvidence(Base):
    __tablename__ = "edge_channel_evidence"
    __table_args__ = (
        UniqueConstraint("tenant_id", "edge_id", "channel", name="uq_edge_channel"),
        ForeignKeyConstraint(
            ["tenant_id", "edge_id"],
            ["edges.tenant_id", "edges.edge_id"],
            ondelete="CASCADE",
            name="fk_edge_channel_evidence_edge",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, default="default", index=True)
    edge_id: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    observation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_observed_at: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)

    edge: Mapped[Any] = relationship("Edge", back_populates="channel_evidence")


class EdgeVersion(Base):
    __tablename__ = "edge_versions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "edge_id"],
            ["edges.tenant_id", "edges.edge_id"],
            ondelete="CASCADE",
            name="fk_edge_versions_edge",
        ),
    )

    version_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, default="default", index=True)
    edge_id: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    layer: Mapped[str] = mapped_column(String(16), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JsonColumn, nullable=False, default=dict)
    valid_from: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)
    valid_to: Mapped[Any | None] = mapped_column(UTCDateTime, nullable=True)
    created_at: Mapped[Any] = mapped_column(UTCDateTime, nullable=False)

    edge: Mapped[Any] = relationship("Edge", back_populates="versions")
