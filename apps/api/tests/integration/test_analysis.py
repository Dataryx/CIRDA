"""Analysis endpoints integration."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analysis_blast_reachability_and_paths(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "an-agent", "entity_type": "agent", "name": "A", "criticality": "low"},
        headers=headers,
    )
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "an-ledger",
            "entity_type": "data",
            "name": "Ledger",
            "criticality": "critical",
        },
        headers=headers,
    )
    for i in range(5):
        await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"an-ev-{i}",
                    "source_id": "an-agent",
                    "target_id": "an-ledger",
                    "relation": "writes",
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            headers=headers,
        )

    blast = await client.post(
        "/api/v1/analysis/blast-radius",
        json={"source_id": "an-agent"},
        headers=headers,
    )
    assert blast.status_code == 200
    assert "an-ledger" in blast.json()["critical_reachable"]

    reach = await client.post(
        "/api/v1/analysis/reachability",
        json={"source_id": "an-agent"},
        headers=headers,
    )
    assert reach.status_code == 200
    assert "an-ledger" in reach.json()["reachable"]

    paths = await client.get(
        "/api/v1/analysis/paths",
        params={"source_id": "an-agent"},
        headers=headers,
    )
    assert paths.status_code == 200
    assert paths.json()["paths"]
