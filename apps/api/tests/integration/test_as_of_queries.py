"""Temporal as_of query tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_graph_as_of(client: AsyncClient) -> None:
    past = datetime.now(timezone.utc) - timedelta(days=1)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "temp-1", "entity_type": "service", "name": "Temporal"},
        headers=headers,
    )
    view = {"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"}
    resp = await client.get("/api/v1/graph", params={"as_of": past.isoformat()}, headers=view)
    assert resp.status_code == 200
    resp2 = await client.get("/api/v1/graph", params={"as_of": future.isoformat()}, headers=view)
    assert resp2.status_code == 200
