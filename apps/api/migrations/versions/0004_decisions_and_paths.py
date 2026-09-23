"""Decisions, decision paths, runbook executions."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decisions",
        sa.Column("decision_id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(128), sa.ForeignKey("entities.entity_id"), nullable=False),
        sa.Column("verdict", sa.String(16), nullable=False),
        sa.Column("coverage", sa.Float(), nullable=False),
        sa.Column("truncated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reason_codes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("rationale", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("as_of", sa.DateTime(timezone=True), nullable=False),
        sa.Column("engine_version", sa.String(16), nullable=False),
        sa.Column("change_type", sa.String(64), nullable=True),
        sa.Column("supersedes_id", sa.String(36), sa.ForeignKey("decisions.decision_id"), nullable=True),
        sa.Column("superseded_by_id", sa.String(36), sa.ForeignKey("decisions.decision_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=True),
    )
    op.create_index("ix_decisions_entity_id", "decisions", ["entity_id"])
    op.create_index("ix_decisions_verdict", "decisions", ["verdict"])
    op.create_index("ix_decisions_as_of", "decisions", ["as_of"])

    op.create_table(
        "decision_paths",
        sa.Column("path_id", sa.String(36), primary_key=True),
        sa.Column("decision_id", sa.String(36), sa.ForeignKey("decisions.decision_id", ondelete="CASCADE"), nullable=False),
        sa.Column("path_nodes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("path_confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("is_critical_path", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_decision_paths_decision_id", "decision_paths", ["decision_id"])

    op.create_table(
        "runbook_executions",
        sa.Column("execution_id", sa.String(36), primary_key=True),
        sa.Column("decision_id", sa.String(36), sa.ForeignKey("decisions.decision_id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_runbook_executions_decision_id", "runbook_executions", ["decision_id"])


def downgrade() -> None:
    op.drop_table("runbook_executions")
    op.drop_table("decision_paths")
    op.drop_table("decisions")
