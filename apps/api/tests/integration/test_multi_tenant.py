"""Multi-tenant isolation (Phase 2: entities, edges, evidence, decisions)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


def _headers(tenant: str, role: str = "analyst") -> dict[str, str]:
    return {
        "Authorization": "Bearer dev",
        "X-CIRDA-Role": role,
        "X-CIRDA-Tenant": tenant,
    }


@pytest.mark.asyncio
async def test_entities_isolated_by_tenant_header(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.multi_tenant_enabled = True

    await client.post(
        "/api/v1/entities",
        json={"entity_id": "shared-id", "entity_type": "agent", "name": "A", "criticality": "low"},
        headers=_headers("tenant-a"),
    )
    await client.post(
        "/api/v1/entities",
        json={"entity_id": "shared-id", "entity_type": "agent", "name": "B", "criticality": "low"},
        headers=_headers("tenant-b"),
    )

    list_a = await client.get("/api/v1/entities", headers=_headers("tenant-a", "viewer"))
    list_b = await client.get("/api/v1/entities", headers=_headers("tenant-b", "viewer"))
    assert list_a.status_code == 200
    assert list_b.status_code == 200
    names_a = {e["name"] for e in list_a.json()["items"] if e["entity_id"] == "shared-id"}
    names_b = {e["name"] for e in list_b.json()["items"] if e["entity_id"] == "shared-id"}
    assert names_a == {"A"}
    assert names_b == {"B"}

    settings.multi_tenant_enabled = False


@pytest.mark.asyncio
async def test_edges_and_evidence_isolated_by_tenant(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.multi_tenant_enabled = True

    now = datetime.now(timezone.utc).isoformat()
    for tenant, name in (("tenant-a", "Alpha"), ("tenant-b", "Beta")):
        headers = _headers(tenant)
        await client.post(
            "/api/v1/entities",
            json={"entity_id": "mt-agent", "entity_type": "agent", "name": name, "criticality": "low"},
            headers=headers,
        )
        await client.post(
            "/api/v1/entities",
            json={
                "entity_id": "mt-ledger",
                "entity_type": "data",
                "name": f"{name}-ledger",
                "criticality": "critical",
            },
            headers=headers,
        )
        await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"{tenant}-ev-1",
                    "source_id": "mt-agent",
                    "target_id": "mt-ledger",
                    "relation": "writes",
                    "observed_at": now,
                },
                "idempotency_key": "shared-idem",
            },
            headers=headers,
        )

    edges_a = await client.get("/api/v1/edges", headers=_headers("tenant-a", "viewer"))
    edges_b = await client.get("/api/v1/edges", headers=_headers("tenant-b", "viewer"))
    assert edges_a.status_code == 200
    assert edges_b.status_code == 200
    assert len(edges_a.json()["items"]) >= 1
    assert len(edges_b.json()["items"]) >= 1
    assert all(e["source_id"] == "mt-agent" for e in edges_a.json()["items"])

    evidence_a = await client.get("/api/v1/evidence", headers=_headers("tenant-a", "viewer"))
    evidence_b = await client.get("/api/v1/evidence", headers=_headers("tenant-b", "viewer"))
    ids_a = {e["event_id"] for e in evidence_a.json()["items"]}
    ids_b = {e["event_id"] for e in evidence_b.json()["items"]}
    assert "tenant-a-ev-1" in ids_a
    assert "tenant-b-ev-1" not in ids_a
    assert "tenant-b-ev-1" in ids_b
    assert "tenant-a-ev-1" not in ids_b

    settings.multi_tenant_enabled = False


@pytest.mark.asyncio
async def test_graph_and_decision_do_not_cross_tenants(client: AsyncClient) -> None:
    transport = client._transport
    app = transport.app  # type: ignore[attr-defined]
    settings = app.state.container.settings
    settings.multi_tenant_enabled = True

    now = datetime.now(timezone.utc).isoformat()
    headers_a = _headers("tenant-a")
    headers_b = _headers("tenant-b")

    for headers, suffix in ((headers_a, "a"), (headers_b, "b")):
        await client.post(
            "/api/v1/entities",
            json={
                "entity_id": "eval-agent",
                "entity_type": "agent",
                "name": f"Agent-{suffix}",
                "criticality": "low",
            },
            headers=headers,
        )
        await client.post(
            "/api/v1/entities",
            json={
                "entity_id": "eval-ledger",
                "entity_type": "data",
                "name": f"Ledger-{suffix}",
                "criticality": "critical",
            },
            headers=headers,
        )

    # Only tenant-a gets the edge
    for i in range(5):
        await client.post(
            "/api/v1/ingest/events",
            json={
                "raw": {
                    "source": "trace",
                    "event_id": f"eval-a-ev-{i}",
                    "source_id": "eval-agent",
                    "target_id": "eval-ledger",
                    "relation": "writes",
                    "observed_at": now,
                }
            },
            headers=headers_a,
        )

    graph_a = await client.get("/api/v1/graph", headers=_headers("tenant-a", "viewer"))
    graph_b = await client.get("/api/v1/graph", headers=_headers("tenant-b", "viewer"))
    assert graph_a.status_code == 200
    assert graph_b.status_code == 200
    assert len(graph_a.json()["edges"]) >= 1
    assert graph_b.json()["edges"] == []

    blast_a = await client.post(
        "/api/v1/analysis/blast-radius",
        json={"source_id": "eval-agent"},
        headers=headers_a,
    )
    blast_b = await client.post(
        "/api/v1/analysis/blast-radius",
        json={"source_id": "eval-agent"},
        headers=headers_b,
    )
    assert blast_a.status_code == 200
    assert blast_b.status_code == 200
    assert "eval-ledger" in blast_a.json()["critical_reachable"]
    assert blast_b.json()["critical_reachable"] == []

    settings.multi_tenant_enabled = False
