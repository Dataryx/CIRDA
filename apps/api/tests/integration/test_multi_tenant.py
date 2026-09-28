"""Multi-tenant entity isolation."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_entities_isolated_by_tenant_header(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.multi_tenant_enabled = True

    headers_a = {
        "Authorization": "Bearer dev",
        "X-CIRDA-Role": "analyst",
        "X-CIRDA-Tenant": "tenant-a",
    }
    headers_b = {
        "Authorization": "Bearer dev",
        "X-CIRDA-Role": "analyst",
        "X-CIRDA-Tenant": "tenant-b",
    }

    await client.post(
        "/api/v1/entities",
        json={"entity_id": "shared-id", "entity_type": "agent", "name": "A", "criticality": "low"},
        headers=headers_a,
    )
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "shared-id", "entity_type": "agent", "name": "B", "criticality": "low"},
        headers=headers_b,
    )

    list_a = await client.get(
        "/api/v1/entities",
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer", "X-CIRDA-Tenant": "tenant-a"},
    )
    list_b = await client.get(
        "/api/v1/entities",
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer", "X-CIRDA-Tenant": "tenant-b"},
    )
    assert list_a.status_code == 200
    assert list_b.status_code == 200
    names_a = {e["name"] for e in list_a.json()["items"] if e["entity_id"] == "shared-id"}
    names_b = {e["name"] for e in list_b.json()["items"] if e["entity_id"] == "shared-id"}
    assert names_a == {"A"}
    assert names_b == {"B"}

    settings.multi_tenant_enabled = False
