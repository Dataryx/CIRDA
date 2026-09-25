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
    assert all("expected_delta_c" in plan for plan in probes)
    assert all(isinstance(plan["expected_delta_c"], (int, float)) for plan in probes)
    # With entities but little/no evidence, ΔC may be 0; shape must still be present.
    assert all(plan["expected_delta_c"] >= 0.0 for plan in probes)

    settings.probe_planning_enabled = False


@pytest.mark.asyncio
async def test_probe_apply_lifts_suppression_when_enabled(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.probe_planning_enabled = True
    settings.probe_execution_enabled = True

    headers_analyst = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    # Populate observed set so restoring a suppressed channel yields positive ΔC.
    for i in range(8):
        await client.post(
            "/api/v1/entities",
            json={
                "entity_id": f"obs-entity-{i}",
                "entity_type": "service",
                "name": f"Observed {i}",
                "criticality": "low",
            },
            headers=headers_analyst,
        )
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "vendor-risk-agent",
            "entity_type": "agent",
            "name": "Vendor Risk",
            "criticality": "high",
        },
        headers=headers_analyst,
    )
    for i in range(6):
        await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"probe-ev-{i}",
                    "source_id": f"obs-entity-{i}",
                    "target_id": f"obs-entity-{(i + 1) % 8}",
                    "relation": "calls",
                    "observed_at": "2026-01-15T12:00:00Z",
                }
            },
            headers=headers_analyst,
        )

    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"}
    evaluate = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "vendor-risk-agent", "change_type": "decommission"},
        headers=headers,
    )
    assert evaluate.status_code == 201
    body = evaluate.json()
    assert body["verdict"] == "INDETERMINATE"
    probes = body["rationale"]["suggested_probes"]
    assert probes
    channel = probes[0]["channels"][0]

    applied = await client.post(
        "/api/v1/decisions/probes/apply",
        json={"entity_id": "vendor-risk-agent", "channels": [channel]},
        headers=headers,
    )
    assert applied.status_code == 200
    result = applied.json()
    assert result["mode"] == "suppression_lift"
    assert channel not in result["suppressed_channels_after"]
    assert result["actual_delta_c"] >= 0.0
    assert abs(result["actual_delta_c"] - result["expected_delta_c"]) < 0.02

    settings.probe_planning_enabled = False
    settings.probe_execution_enabled = False


@pytest.mark.asyncio
async def test_probe_apply_forbidden_when_execution_disabled(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.probe_planning_enabled = True
    settings.probe_execution_enabled = False

    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"}
    response = await client.post(
        "/api/v1/decisions/probes/apply",
        json={"entity_id": "vendor-risk-agent", "channels": ["database"]},
        headers=headers,
    )
    assert response.status_code == 403

    settings.probe_planning_enabled = False
