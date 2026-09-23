"""OpenAPI contract snapshot test."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from httpx import AsyncClient

SNAPSHOT = Path(__file__).parent / "openapi.snapshot.json"


@pytest.mark.asyncio
async def test_openapi_schema_keys(client: AsyncClient) -> None:
    resp = await client.get("/openapi.json", headers={"Authorization": "Bearer dev"})
    assert resp.status_code == 200
    schema = resp.json()
    paths = schema.get("paths", {})
    expected_prefixes = (
        "/api/v1/health",
        "/api/v1/ingest/events",
        "/api/v1/entities",
        "/api/v1/graph",
        "/api/v1/decisions/evaluate",
        "/api/v1/coverage",
        "/api/v1/benchmarks/runs",
    )
    for prefix in expected_prefixes:
        assert any(p.startswith(prefix.rstrip("/")) or p == prefix for p in paths), f"missing {prefix}"

    verdict_enum = schema["components"]["schemas"]["VerdictSchema"]["enum"]
    assert set(verdict_enum) == {"UNSAFE", "SAFE", "INDETERMINATE"}

    if not SNAPSHOT.exists():
        SNAPSHOT.write_text(json.dumps({"paths": sorted(paths.keys())}, indent=2), encoding="utf-8")
    else:
        saved = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        assert saved["paths"] == sorted(paths.keys())
