"""Audit log, benchmark runs/results, principals."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "benchmark_runs",
        sa.Column("run_id", sa.String(36), primary_key=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_benchmark_runs_status", "benchmark_runs", ["status"])

    op.create_table(
        "benchmark_results",
        sa.Column("result_id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("benchmark_runs.run_id", ondelete="CASCADE"), nullable=False),
        sa.Column("loss", sa.Float(), nullable=False),
        sa.Column("method", sa.String(32), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("data_class", sa.String(64), nullable=False, server_default="synthetic_benchmark"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_benchmark_results_run_id", "benchmark_results", ["run_id"])

    op.create_table(
        "audit_log",
        sa.Column("log_id", sa.String(36), primary_key=True),
        sa.Column("principal_id", sa.String(128), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.String(128), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ip_address", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_log_principal_id", "audit_log", ["principal_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])

    op.create_table(
        "principals",
        sa.Column("principal_id", sa.String(128), primary_key=True),
        sa.Column("subject", sa.String(256), nullable=False, unique=True),
        sa.Column("roles", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("api_key_hash", sa.String(256), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("principals")
    op.drop_table("audit_log")
    op.drop_table("benchmark_results")
    op.drop_table("benchmark_runs")
