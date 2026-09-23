"""Graph endpoint tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_graph_returns_payload(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "a1", "entity_type": "agent", "name": "Agent A"},
        headers=headers,
    )
    await client.post(
        "/api/v1/ingest/events",
        json={
            "raw": {
                "source": "trace",
                "event_id": "g-1",
                "source_id": "a1",
                "target_id": "t1",
                "relation": "calls",
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=headers,
    )
    resp = await client.get("/api/v1/graph", headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"})
    assert resp.status_code == 200
    body = resp.json()
    assert "nodes" in body
    assert "edges" in body
    assert body["engine_version"]
