"""Coverage gate tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_coverage_estimate(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/coverage", headers={"Authorization": "Bearer dev", "X-CIRDA-Role": "viewer"})
    assert resp.status_code == 200
    body = resp.json()
    assert 0.0 <= body["coverage"] <= 1.0
    assert "c_min" in body
    assert "meets_threshold" in body
