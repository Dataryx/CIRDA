"""Coverage snapshots, channel health, calibration profiles."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "coverage_snapshots",
        sa.Column("snapshot_id", sa.String(36), primary_key=True),
        sa.Column("coverage", sa.Float(), nullable=False),
        sa.Column("observed_entities", sa.Integer(), nullable=False),
        sa.Column("total_entities", sa.Integer(), nullable=False),
        sa.Column("suppressed_channels", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("scope", sa.String(128), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_coverage_snapshots_captured_at", "coverage_snapshots", ["captured_at"])

    op.create_table(
        "channel_health",
        sa.Column("channel", sa.String(32), primary_key=True),
        sa.Column("health_score", sa.Float(), nullable=False, server_default="1"),
        sa.Column("lag_seconds", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("details", sa.String(512), nullable=True),
    )

    op.create_table(
        "calibration_profiles",
        sa.Column("profile_id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("theta_c", sa.Float(), nullable=False),
        sa.Column("theta_p", sa.Float(), nullable=False),
        sa.Column("c_min", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("calibration_profiles")
    op.drop_table("channel_health")
    op.drop_table("coverage_snapshots")
