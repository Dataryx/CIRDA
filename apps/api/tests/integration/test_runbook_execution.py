"""Runbook execution tracking integration tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_evaluate_seeds_runbook_and_stage_can_advance(client: AsyncClient) -> None:
    from datetime import datetime, timezone

    headers_analyst = {"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"}
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "runbook-safe-agent",
            "entity_type": "agent",
            "name": "Runbook Safe",
            "criticality": "low",
        },
        headers=headers_analyst,
    )
    # Pad estate so coverage can meet C_min for an isolated agent.
    for i in range(10):
        await client.post(
            "/api/v1/entities",
            json={
                "entity_id": f"rb-pad-{i}",
                "entity_type": "service",
                "name": f"Pad {i}",
                "criticality": "low",
            },
            headers=headers_analyst,
        )
        await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"rb-pad-ev-{i}",
                    "source_id": f"rb-pad-{i}",
                    "target_id": f"rb-pad-{(i + 1) % 10}",
                    "relation": "calls",
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            headers=headers_analyst,
        )

    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"}
    evaluate = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "runbook-safe-agent", "change_type": "retirement"},
        headers=headers,
    )
    assert evaluate.status_code == 201
    body = evaluate.json()
    assert body["verdict"] in ("SAFE", "INDETERMINATE")
    executions = body["runbook_executions"]
    assert executions
    assert all(e["status"] == "pending" for e in executions)
    if body["verdict"] == "SAFE":
        assert len(executions) >= 5

    decision_id = body["decision_id"]
    first = executions[0]
    started = await client.patch(
        f"/api/v1/decisions/{decision_id}/runbook/{first['execution_id']}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert started.status_code == 200
    assert started.json()["status"] == "in_progress"
    assert started.json()["started_at"] is not None

    completed = await client.patch(
        f"/api/v1/decisions/{decision_id}/runbook/{first['execution_id']}",
        json={"status": "completed", "notes": "done"},
        headers=headers,
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["completed_at"] is not None

    listed = await client.get(
        f"/api/v1/decisions/{decision_id}/runbook",
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"},
    )
    assert listed.status_code == 200
    by_id = {e["execution_id"]: e for e in listed.json()["items"]}
    assert by_id[first["execution_id"]]["status"] == "completed"


@pytest.mark.asyncio
async def test_runbook_rejects_invalid_transition(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/entities",
        json={
            "entity_id": "runbook-bad-agent",
            "entity_type": "agent",
            "name": "Runbook Bad",
            "criticality": "low",
        },
        headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "analyst"},
    )
    headers = {"Authorization": "Bearer dev", "X-CIRDA-Role": "approver"}
    evaluate = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "runbook-bad-agent"},
        headers=headers,
    )
    body = evaluate.json()
    execution_id = body["runbook_executions"][0]["execution_id"]
    # Jumping pending → completed is allowed; completed → in_progress is not.
    await client.patch(
        f"/api/v1/decisions/{body['decision_id']}/runbook/{execution_id}",
        json={"status": "completed"},
        headers=headers,
    )
    bad = await client.patch(
        f"/api/v1/decisions/{body['decision_id']}/runbook/{execution_id}",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert bad.status_code == 400
