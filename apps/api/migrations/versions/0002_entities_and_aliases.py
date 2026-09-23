"""Entities and aliases tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entities",
        sa.Column("entity_id", sa.String(128), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("name", sa.String(512), nullable=False),
        sa.Column("criticality", sa.String(16), nullable=False, server_default="unknown"),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_entities_entity_type", "entities", ["entity_type"])
    op.create_table(
        "aliases",
        sa.Column("alias_id", sa.String(36), primary_key=True),
        sa.Column("entity_id", sa.String(128), sa.ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(512), nullable=False),
        sa.Column("source", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("entity_id", "alias", name="uq_alias_entity_alias"),
    )
    op.create_index("ix_aliases_entity_id", "aliases", ["entity_id"])
    op.create_index("ix_aliases_alias", "aliases", ["alias"])


def downgrade() -> None:
    op.drop_table("aliases")
    op.drop_table("entities")
