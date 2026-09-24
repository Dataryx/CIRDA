"""Ingest idempotency integration tests."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ingest_idempotency(client: AsyncClient) -> None:
    raw = {
        "source": "trace",
        "event_id": "evt-1",
        "source_id": "agent-a",
        "target_id": "tool-b",
        "relation": "calls",
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    r1 = await client.post("/api/v1/ingest/events", json={"raw": raw, "idempotency_key": "key-1"}, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["created"] is True

    r2 = await client.post("/api/v1/ingest/events", json={"raw": raw, "idempotency_key": "key-1"}, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["created"] is False
    assert r2.json()["event"]["event_id"] == r1.json()["event"]["event_id"]


@pytest.mark.asyncio
async def test_ingest_duplicate_event_id_is_idempotent(client: AsyncClient) -> None:
    raw = {
        "source": "trace",
        "event_id": "evt-dup-id",
        "source_id": "agent-a",
        "target_id": "tool-b",
        "relation": "calls",
        "observed_at": datetime.now(timezone.utc).isoformat(),
    }
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    r1 = await client.post("/api/v1/ingest/events", json={"raw": raw}, headers=headers)
    assert r1.status_code == 200
    assert r1.json()["created"] is True

    r2 = await client.post("/api/v1/ingest/events", json={"raw": raw}, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["created"] is False
    assert r2.json()["event"]["event_id"] == "evt-dup-id"
