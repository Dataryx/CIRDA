"""Necessity suggestion integration tests (suggest-only)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_necessity_suggestions_bridge_and_optional(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    for eid, etype, crit in (
        ("hint-agent", "agent", "low"),
        ("hint-ledger", "data", "critical"),
        ("hint-queue", "queue", "low"),
    ):
        await client.post(
            "/api/v1/entities",
            json={
                "entity_id": eid,
                "entity_type": etype,
                "name": eid,
                "criticality": crit,
            },
            headers=headers,
        )

    for i, (src, tgt, relation) in enumerate(
        (
            ("hint-agent", "hint-ledger", "writes"),
            ("hint-agent", "hint-queue", "publishes"),
        )
    ):
        for j in range(4):
            await client.post(
                "/api/v1/ingest/events",
                json={
                    "raw": {
                        "source": "trace",
                        "event_id": f"hint-ev-{i}-{j}",
                        "source_id": src,
                        "target_id": tgt,
                        "relation": relation,
                        "observed_at": datetime.now(timezone.utc).isoformat(),
                    }
                },
                headers=headers,
            )

    response = await client.get(
        "/api/v1/edges/necessity-suggestions",
        params={"source_id": "hint-agent"},
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "suggest_only"
    assert body["source_id"] == "hint-agent"
    by_edge = {item["edge_id"]: item for item in body["items"]}
    assert "hint-agent->hint-ledger:writes" in by_edge
    assert by_edge["hint-agent->hint-ledger:writes"]["suggested_necessity"] == "required"
    assert "hint-agent->hint-queue:publishes" in by_edge
    assert by_edge["hint-agent->hint-queue:publishes"]["suggested_necessity"] == "optional"

    # Accept optional hint via PATCH; suggestions for that edge disappear.
    accept = await client.patch(
        "/api/v1/edges/hint-agent->hint-queue:publishes",
        json={"necessity": "optional"},
        headers=headers,
    )
    assert accept.status_code == 200
    after = await client.get(
        "/api/v1/edges/necessity-suggestions",
        params={"source_id": "hint-agent"},
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"},
    )
    remaining = {item["edge_id"] for item in after.json()["items"]}
    assert "hint-agent->hint-queue:publishes" not in remaining
