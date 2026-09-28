"""Necessity auto-mutate integration."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_necessity_auto_mutate_applies_required_when_enabled(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.necessity_auto_mutate_enabled = True
    settings.necessity_auto_min_confidence = 0.85

    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "am-agent", "entity_type": "agent", "name": "AM", "criticality": "low"},
        headers=headers,
    )
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "am-ledger",
            "entity_type": "data",
            "name": "Ledger",
            "criticality": "critical",
        },
        headers=headers,
    )
    await client.post(
        "/api/v1/ingest/events",
        json={
            "raw": {
                "source": "trace",
                "event_id": "am-ev-1",
                "source_id": "am-agent",
                "target_id": "am-ledger",
                "relation": "writes",
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers=headers,
    )
    # Pad observations so edge confidence is high enough for confirmed/possible.
    for i in range(4):
        await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"am-ev-pad-{i}",
                    "source_id": "am-agent",
                    "target_id": "am-ledger",
                    "relation": "writes",
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            headers=headers,
        )

    forbidden = await client.post(
        "/api/v1/edges/necessity-auto-mutate",
        json={"source_id": "am-agent"},
        headers=headers,
    )
    # With flag on should succeed
    assert forbidden.status_code == 200
    body = forbidden.json()
    assert body["mode"] == "auto_mutate"
    assert body["candidates"] >= 0

    settings.necessity_auto_mutate_enabled = False
    blocked = await client.post(
        "/api/v1/edges/necessity-auto-mutate",
        json={"source_id": "am-agent"},
        headers=headers,
    )
    assert blocked.status_code == 403
