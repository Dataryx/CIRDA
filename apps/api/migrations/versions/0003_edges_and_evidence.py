"""Edges, channel evidence, evidence events, edge versions."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "edges",
        sa.Column("edge_id", sa.String(256), primary_key=True),
        sa.Column("source_id", sa.String(128), sa.ForeignKey("entities.entity_id"), nullable=False),
        sa.Column("target_id", sa.String(128), sa.ForeignKey("entities.entity_id"), nullable=False),
        sa.Column("relation", sa.String(32), nullable=False),
        sa.Column("layer", sa.String(16), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("necessity", sa.String(16), nullable=False, server_default="unknown"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_edges_source_id", "edges", ["source_id"])
    op.create_index("ix_edges_target_id", "edges", ["target_id"])
    op.create_index("ix_edges_layer", "edges", ["layer"])

    op.create_table(
        "edge_channel_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("edge_id", sa.String(256), sa.ForeignKey("edges.edge_id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("observation_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("edge_id", "channel", name="uq_edge_channel"),
    )
    op.create_index("ix_edge_channel_evidence_edge_id", "edge_channel_evidence", ["edge_id"])

    op.create_table(
        "evidence_events",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("idempotency_key", sa.String(256), nullable=True),
        sa.Column("source_id", sa.String(128), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=False),
        sa.Column("relation", sa.String(32), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=True),
        sa.Column("target_type", sa.String(32), nullable=True),
        sa.Column("payload_hash", sa.String(128), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_evidence_idempotency"),
    )
    op.create_index("ix_evidence_events_source_id", "evidence_events", ["source_id"])
    op.create_index("ix_evidence_events_target_id", "evidence_events", ["target_id"])
    op.create_index("ix_evidence_events_channel", "evidence_events", ["channel"])
    op.create_index("ix_evidence_events_observed_at", "evidence_events", ["observed_at"])
    op.create_index("ix_evidence_events_idempotency_key", "evidence_events", ["idempotency_key"])

    op.create_table(
        "edge_versions",
        sa.Column("version_id", sa.String(36), primary_key=True),
        sa.Column("edge_id", sa.String(256), sa.ForeignKey("edges.edge_id", ondelete="CASCADE"), nullable=False),
        sa.Column("layer", sa.String(16), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_edge_versions_edge_id", "edge_versions", ["edge_id"])


def downgrade() -> None:
    op.drop_table("edge_versions")
    op.drop_table("evidence_events")
    op.drop_table("edge_channel_evidence")
    op.drop_table("edges")
