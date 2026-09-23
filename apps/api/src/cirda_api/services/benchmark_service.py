"""Benchmark orchestration service."""

from __future__ import annotations

from typing import Any

from cirda_api.db.repositories.benchmark import BenchmarkRepository


class BenchmarkService:
    def __init__(self, repo: BenchmarkRepository) -> None:
        self.repo = repo

    async def create_run(self, config: dict[str, Any]) -> dict[str, Any]:
        return await self.repo.create_run(config)

    async def get_run(self, run_id: str) -> dict[str, Any] | None:
        return await self.repo.get_run(run_id)

    async def list_runs(self, *, offset: int = 0, limit: int = 20) -> tuple[list[dict[str, Any]], int]:
        return await self.repo.list_runs(offset=offset, limit=limit)

    async def get_results(self, run_id: str) -> list[dict[str, Any]]:
        return await self.repo.list_results(run_id)

    async def seed_demo_results(self, run_id: str) -> None:
        """Populate synthetic benchmark rows for API contract tests."""
        await self.repo.update_run_status(run_id, "running")
        demo_rows = [
            (0.30, "cirda", {"edge_f1": 0.947, "false_safe": 0.0, "decision_coverage": 0.956}),
            (0.45, "cirda", {"edge_f1": 0.903, "false_safe": 0.0, "decision_coverage": 0.943}),
        ]
        for loss, method, metrics in demo_rows:
            await self.repo.add_result(run_id, loss=loss, method=method, metrics=metrics)
        await self.repo.update_run_status(run_id, "completed")
