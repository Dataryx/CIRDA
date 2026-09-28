"""Add tenant_id columns for multi-tenant logical isolation."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

_TABLES = (
    "entities",
    "aliases",
    "edges",
    "evidence_events",
    "decisions",
    "coverage_snapshots",
    "channel_health",
    "audit_log",
    "benchmark_runs",
)


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(
            table,
            sa.Column(
                "tenant_id",
                sa.String(length=128),
                nullable=False,
                server_default="default",
            ),
        )
        op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"])


def downgrade() -> None:
    for table in reversed(_TABLES):
        op.drop_index(f"ix_{table}_tenant_id", table_name=table)
        op.drop_column(table, "tenant_id")
