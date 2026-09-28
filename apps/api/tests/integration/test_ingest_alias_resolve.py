"""Ingest resolves unique aliases to canonical entity ids."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ingest_resolves_unique_alias_to_canonical(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}

    create = await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "canonical-agent",
            "entity_type": "agent",
            "name": "Canonical Agent",
            "criticality": "low",
            "aliases": ["alias_agent"],
        },
        headers=headers,
    )
    assert create.status_code == 201

    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "canonical-db",
            "entity_type": "data",
            "name": "Canonical DB",
            "criticality": "medium",
        },
        headers=headers,
    )

    ingest = await client.post(
        "/api/v1/ingest/events",
        json={
            "raw": {
                "source": "agent_framework",
                "channel": "agent_framework",
                "event_id": "alias-resolve-ev-1",
                "agent_id": "alias_agent",
                "target_id": "canonical-db",
                "action": "call",
                "relation": "reads",
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=headers,
    )
    assert ingest.status_code == 200
    body = ingest.json()
    assert body["created"] is True
    assert body["event"]["source_id"] == "canonical-agent"
    assert body["event"]["target_id"] == "canonical-db"
    assert body.get("resolved_from") == {
        "source_id": "alias_agent",
        "target_id": "canonical-db",
    }

    orphan = await client.get(
        "/api/v1/entities/alias_agent",
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"},
    )
    assert orphan.status_code == 404

    # No split-identity from resolved ingest alone.
    evaluate = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "canonical-agent", "change_type": "retirement"},
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"},
    )
    assert evaluate.status_code == 201
    assert "ambiguous_identity" not in evaluate.json()["reason_codes"]


@pytest.mark.asyncio
async def test_ingest_passthrough_when_alias_collision(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}

    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "owner-a",
            "entity_type": "agent",
            "name": "Owner A",
            "criticality": "low",
            "aliases": ["shared_alias"],
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "owner-b",
            "entity_type": "agent",
            "name": "Owner B",
            "criticality": "low",
            "aliases": ["shared_alias"],
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "collision-db",
            "entity_type": "data",
            "name": "Collision DB",
            "criticality": "low",
        },
        headers=headers,
    )

    ingest = await client.post(
        "/api/v1/ingest/events",
        json={
            "raw": {
                "source": "trace",
                "event_id": "alias-collision-ev-1",
                "source_id": "shared_alias",
                "target_id": "collision-db",
                "relation": "reads",
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=headers,
    )
    assert ingest.status_code == 200
    body = ingest.json()
    # Ambiguous alias → passthrough (may create orphan shared_alias entity).
    assert body["event"]["source_id"] == "shared_alias"
    assert body.get("resolved_from") is None

    evaluate = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "owner-a", "change_type": "retirement"},
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"},
    )
    assert evaluate.status_code == 201
    assert "ambiguous_identity" in evaluate.json()["reason_codes"]
