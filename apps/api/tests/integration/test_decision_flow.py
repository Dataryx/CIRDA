"""Decision flow integration tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_decision_evaluate_and_rerun(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "retire-me", "entity_type": "agent", "name": "Retire Me", "criticality": "low"},
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"},
    )
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"}
    r1 = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "retire-me", "change_type": "retirement"},
        headers=headers,
    )
    assert r1.status_code == 201
    body = r1.json()
    assert body["verdict"] in ("UNSAFE", "SAFE", "INDETERMINATE")
    assert body["limitations_footer"]
    assert "rationale" in body
    assert body["rationale"].get("suggested_probes") == []

    d1 = body["decision_id"]
    r2 = await client.post(f"/api/v1/decisions/{d1}/rerun", headers=headers)
    assert r2.status_code == 201
    body2 = r2.json()
    assert body2["supersedes"] == d1
    assert body2["decision_id"] != d1


@pytest.mark.asyncio
async def test_indeterminate_vendor_risk_suggests_probes_when_enabled(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.probe_planning_enabled = True

    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "vendor-risk-agent",
            "entity_type": "agent",
            "name": "Vendor Risk",
            "criticality": "high",
        },
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"},
    )
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"}
    response = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "vendor-risk-agent", "change_type": "decommission"},
        headers=headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["verdict"] == "INDETERMINATE"
    probes = body["rationale"]["suggested_probes"]
    assert probes
    channels = {ch for plan in probes for ch in plan["channels"]}
    assert "database" in channels
    assert "messaging" in channels
    assert all(plan["entity_id"] == "vendor-risk-agent" for plan in probes)
    assert all(plan["rationale"] for plan in probes)

    settings.probe_planning_enabled = False
