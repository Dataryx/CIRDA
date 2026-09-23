"""Benchmark response data_class unit test."""

from __future__ import annotations

import pytest

from cirda_api.container import build_container
from cirda_api.settings import Settings


@pytest.mark.asyncio
async def test_benchmark_results_include_data_class() -> None:
    settings = Settings(memory_store=True, scheduler_enabled=False)
    container = build_container(settings)
    run = await container.benchmark_service.create_run({"seed_demo": False})
    await container.benchmark_service.seed_demo_results(run["run_id"])
    results = await container.benchmark_service.get_results(run["run_id"])
    assert results
    assert all(r["data_class"] == "synthetic_benchmark" for r in results)
