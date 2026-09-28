"""Composite tenant PKs and tenant-scoped foreign keys (Phase 2)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Drop FKs that reference entities.entity_id alone ---
    op.drop_constraint("aliases_entity_id_fkey", "aliases", type_="foreignkey")
    op.drop_constraint("uq_alias_entity_alias", "aliases", type_="unique")
    op.drop_constraint("edges_source_id_fkey", "edges", type_="foreignkey")
    op.drop_constraint("edges_target_id_fkey", "edges", type_="foreignkey")
    op.drop_constraint("decisions_entity_id_fkey", "decisions", type_="foreignkey")
    op.drop_constraint("edge_channel_evidence_edge_id_fkey", "edge_channel_evidence", type_="foreignkey")
    op.drop_constraint("uq_edge_channel", "edge_channel_evidence", type_="unique")
    op.drop_constraint("edge_versions_edge_id_fkey", "edge_versions", type_="foreignkey")
    op.drop_constraint("uq_evidence_idempotency", "evidence_events", type_="unique")

    # --- entities: composite PK (tenant_id, entity_id) ---
    op.drop_constraint("entities_pkey", "entities", type_="primary")
    op.create_primary_key("pk_entities", "entities", ["tenant_id", "entity_id"])

    # --- aliases ---
    op.create_unique_constraint(
        "uq_alias_tenant_entity_alias", "aliases", ["tenant_id", "entity_id", "alias"]
    )
    op.create_foreign_key(
        "fk_aliases_entity",
        "aliases",
        "entities",
        ["tenant_id", "entity_id"],
        ["tenant_id", "entity_id"],
        ondelete="CASCADE",
    )

    # --- edges: composite PK ---
    op.drop_constraint("edges_pkey", "edges", type_="primary")
    op.create_primary_key("pk_edges", "edges", ["tenant_id", "edge_id"])
    op.create_foreign_key(
        "fk_edges_source",
        "edges",
        "entities",
        ["tenant_id", "source_id"],
        ["tenant_id", "entity_id"],
    )
    op.create_foreign_key(
        "fk_edges_target",
        "edges",
        "entities",
        ["tenant_id", "target_id"],
        ["tenant_id", "entity_id"],
    )

    # --- edge children: add tenant_id (backfill from edges) ---
    op.add_column(
        "edge_channel_evidence",
        sa.Column("tenant_id", sa.String(128), nullable=False, server_default="default"),
    )
    op.execute(
        """
        UPDATE edge_channel_evidence AS ece
        SET tenant_id = e.tenant_id
        FROM edges AS e
        WHERE ece.edge_id = e.edge_id
        """
    )
    op.create_index("ix_edge_channel_evidence_tenant_id", "edge_channel_evidence", ["tenant_id"])
    op.create_unique_constraint(
        "uq_edge_channel", "edge_channel_evidence", ["tenant_id", "edge_id", "channel"]
    )
    op.create_foreign_key(
        "fk_edge_channel_evidence_edge",
        "edge_channel_evidence",
        "edges",
        ["tenant_id", "edge_id"],
        ["tenant_id", "edge_id"],
        ondelete="CASCADE",
    )

    op.add_column(
        "edge_versions",
        sa.Column("tenant_id", sa.String(128), nullable=False, server_default="default"),
    )
    op.execute(
        """
        UPDATE edge_versions AS ev
        SET tenant_id = e.tenant_id
        FROM edges AS e
        WHERE ev.edge_id = e.edge_id
        """
    )
    op.create_index("ix_edge_versions_tenant_id", "edge_versions", ["tenant_id"])
    op.create_foreign_key(
        "fk_edge_versions_edge",
        "edge_versions",
        "edges",
        ["tenant_id", "edge_id"],
        ["tenant_id", "edge_id"],
        ondelete="CASCADE",
    )

    # --- decisions ---
    op.create_foreign_key(
        "fk_decisions_entity",
        "decisions",
        "entities",
        ["tenant_id", "entity_id"],
        ["tenant_id", "entity_id"],
    )

    # --- evidence idempotency scoped by tenant ---
    op.create_unique_constraint(
        "uq_evidence_tenant_idempotency",
        "evidence_events",
        ["tenant_id", "idempotency_key"],
    )

    # --- channel_health composite PK ---
    op.drop_constraint("channel_health_pkey", "channel_health", type_="primary")
    op.create_primary_key("pk_channel_health", "channel_health", ["tenant_id", "channel"])


def downgrade() -> None:
    op.drop_constraint("pk_channel_health", "channel_health", type_="primary")
    op.create_primary_key("channel_health_pkey", "channel_health", ["channel"])

    op.drop_constraint("uq_evidence_tenant_idempotency", "evidence_events", type_="unique")
    op.create_unique_constraint("uq_evidence_idempotency", "evidence_events", ["idempotency_key"])

    op.drop_constraint("fk_decisions_entity", "decisions", type_="foreignkey")
    op.create_foreign_key(
        "decisions_entity_id_fkey", "decisions", "entities", ["entity_id"], ["entity_id"]
    )

    op.drop_constraint("fk_edge_versions_edge", "edge_versions", type_="foreignkey")
    op.drop_index("ix_edge_versions_tenant_id", table_name="edge_versions")
    op.drop_column("edge_versions", "tenant_id")
    op.create_foreign_key(
        "edge_versions_edge_id_fkey",
        "edge_versions",
        "edges",
        ["edge_id"],
        ["edge_id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("fk_edge_channel_evidence_edge", "edge_channel_evidence", type_="foreignkey")
    op.drop_constraint("uq_edge_channel", "edge_channel_evidence", type_="unique")
    op.drop_index("ix_edge_channel_evidence_tenant_id", table_name="edge_channel_evidence")
    op.drop_column("edge_channel_evidence", "tenant_id")
    op.create_unique_constraint("uq_edge_channel", "edge_channel_evidence", ["edge_id", "channel"])
    op.create_foreign_key(
        "edge_channel_evidence_edge_id_fkey",
        "edge_channel_evidence",
        "edges",
        ["edge_id"],
        ["edge_id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("fk_edges_source", "edges", type_="foreignkey")
    op.drop_constraint("fk_edges_target", "edges", type_="foreignkey")
    op.drop_constraint("pk_edges", "edges", type_="primary")
    op.create_primary_key("edges_pkey", "edges", ["edge_id"])
    op.create_foreign_key(
        "edges_source_id_fkey", "edges", "entities", ["source_id"], ["entity_id"]
    )
    op.create_foreign_key(
        "edges_target_id_fkey", "edges", "entities", ["target_id"], ["entity_id"]
    )

    op.drop_constraint("fk_aliases_entity", "aliases", type_="foreignkey")
    op.drop_constraint("uq_alias_tenant_entity_alias", "aliases", type_="unique")
    op.create_unique_constraint("uq_alias_entity_alias", "aliases", ["entity_id", "alias"])
    op.create_foreign_key(
        "aliases_entity_id_fkey",
        "aliases",
        "entities",
        ["entity_id"],
        ["entity_id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("pk_entities", "entities", type_="primary")
    op.create_primary_key("entities_pkey", "entities", ["entity_id"])
