"""Multi-tenant isolation against a migrated PostgreSQL database.

Set ``CIRDA_TEST_DATABASE_URL`` (asyncpg URL, schema at ``alembic upgrade head``)
to run; skipped otherwise.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cirda_api.db.repositories.edge import EdgeRepository
from cirda_api.db.repositories.entity import EntityRepository
from cirda_api.db.repositories.evidence import EvidenceRepository
from cirda_api.security.tenant import set_current_tenant_id
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Relation
from cirda_core.domain.event import EvidenceEvent

DATABASE_URL = os.environ.get("CIRDA_TEST_DATABASE_URL")

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not DATABASE_URL, reason="CIRDA_TEST_DATABASE_URL not set"),
]


@pytest.mark.asyncio
async def test_same_ids_coexist_across_tenants_on_postgres() -> None:
    engine = create_async_engine(DATABASE_URL)  # type: ignore[arg-type]
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    suffix = uuid.uuid4().hex[:8]
    tenant_a, tenant_b = f"pg-a-{suffix}", f"pg-b-{suffix}"
    now = datetime.now(timezone.utc)

    try:
        for tenant, name in ((tenant_a, "Alpha"), (tenant_b, "Beta")):
            set_current_tenant_id(tenant)
            async with sessions() as session:
                entities = EntityRepository(session=session)
                await entities.upsert_entity(
                    entity_id="shared-agent", entity_type="agent", name=name, aliases=["shared-alias"]
                )
                await entities.upsert_entity(
                    entity_id="shared-db", entity_type="data", name=f"{name}-db", criticality="critical"
                )
                await EdgeRepository(session=session).upsert_edge(
                    DependencyEdge(
                        edge_id="shared-agent->shared-db:writes",
                        source_id="shared-agent",
                        target_id="shared-db",
                        relation=Relation.WRITES,
                        layer=GraphLayer.CONFIRMED,
                        confidence=0.9 if tenant == tenant_a else 0.4,
                    )
                )
                await EvidenceRepository(session=session).add_event(
                    EvidenceEvent(
                        event_id=f"ev-{tenant}",
                        source_id="shared-agent",
                        target_id="shared-db",
                        relation=Relation.WRITES,
                        channel=EvidenceChannel.DATABASE,
                        observed_at=now,
                    ),
                    idempotency_key=f"idem-{suffix}",
                )

        for tenant, name, confidence in ((tenant_a, "Alpha", 0.9), (tenant_b, "Beta", 0.4)):
            set_current_tenant_id(tenant)
            async with sessions() as session:
                entity = await EntityRepository(session=session).get_entity("shared-agent")
                assert entity is not None
                assert entity["name"] == name
                assert entity["aliases"] == ["shared-alias"]
                assert await EntityRepository(session=session).find_entity_ids_by_alias(
                    "shared-alias"
                ) == {"shared-agent"}

                edge = await EdgeRepository(session=session).get_edge("shared-agent->shared-db:writes")
                assert edge is not None
                assert edge["confidence"] == pytest.approx(confidence)

                events, total = await EvidenceRepository(session=session).list_events(
                    source_id="shared-agent"
                )
                assert total == 1
                assert events[0]["event_id"] == f"ev-{tenant}"
    finally:
        set_current_tenant_id("default")
        await engine.dispose()
