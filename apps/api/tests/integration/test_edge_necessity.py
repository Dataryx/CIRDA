"""Edge necessity annotation integration tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_patch_edge_necessity_and_preserve_on_reingest(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "agent-n",
            "entity_type": "agent",
            "name": "Agent N",
            "criticality": "high",
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "svc-n",
            "entity_type": "service",
            "name": "Service N",
            "criticality": "critical",
        },
        headers=headers,
    )
    # Multiple observations so fusion clears θ_p and creates a possible-layer edge.
    for i in range(4):
        ingested = await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"necessity-evt-{i}",
                    "source_id": "agent-n",
                    "target_id": "svc-n",
                    "relation": "writes",
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            headers=headers,
        )
        assert ingested.status_code == 200
    assert ingested.json().get("edge_updated") is True

    listed = await client.get(
        "/api/v1/edges",
        params={"source_id": "agent-n", "target_id": "svc-n"},
        headers=headers,
    )
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert items, "expected an edge after ingest"
    edge_id = items[0]["edge_id"]

    # Path params with "->" must be URL-encoded; httpx does this automatically.
    patched = await client.patch(
        f"/api/v1/edges/{edge_id}",
        json={"necessity": "optional"},
        headers=headers,
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["necessity"] == "optional"

    # Re-ingest must not wipe operator annotation when fusion yields unknown.
    reingest = await client.post(
        "/api/v1/ingest/events",
        json={
            "raw": {
                "source": "trace",
                "event_id": "necessity-evt-reingest",
                "source_id": "agent-n",
                "target_id": "svc-n",
                "relation": "writes",
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=headers,
    )
    assert reingest.status_code == 200

    got = await client.get(f"/api/v1/edges/{edge_id}", headers=headers)
    assert got.status_code == 200, got.text
    assert got.json()["necessity"] == "optional"


@pytest.mark.asyncio
async def test_patch_edge_necessity_rejects_invalid(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    response = await client.patch(
        "/api/v1/edges/missing-edge",
        json={"necessity": "not-a-value"},
        headers=headers,
    )
    assert response.status_code == 400
