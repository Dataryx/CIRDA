"""RBAC and redaction tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_viewer_cannot_evaluate_decision(client: AsyncClient, viewer_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/api/v1/decisions/evaluate",
        json={"entity_id": "x"},
        headers=viewer_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_viewer_can_read_health(client: AsyncClient, viewer_headers: dict[str, str]) -> None:
    resp = await client.get("/api/v1/health", headers=viewer_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_rejected(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/entities", headers={})
    assert resp.status_code == 401
