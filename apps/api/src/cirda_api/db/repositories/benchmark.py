"""Benchmark repository."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.benchmark import BenchmarkResult, BenchmarkRun
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore


class BenchmarkRepository(RepositoryBase):
    async def create_run(self, config: dict[str, Any]) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        now = utcnow()
        record = {"run_id": run_id, "status": "pending", "config": config, "created_at": now}
        if self.memory:
            self.memory.benchmark_runs[run_id] = record
            self.memory.benchmark_results[run_id] = []
            return record

        assert self.session is not None
        row = BenchmarkRun(run_id=run_id, status="pending", config=config, created_at=now)
        self.session.add(row)
        await self.session.commit()
        return record

    async def get_run(self, run_id: str) -> dict[str, Any] | None:
        if self.memory:
            return self.memory.benchmark_runs.get(run_id)

        assert self.session is not None
        row = await self.session.get(BenchmarkRun, run_id)
        if not row:
            return None
        return {
            "run_id": row.run_id,
            "status": row.status,
            "config": row.config,
            "started_at": row.started_at,
            "completed_at": row.completed_at,
            "error_message": row.error_message,
            "created_at": row.created_at,
        }

    async def list_runs(self, *, offset: int = 0, limit: int = 20) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = list(self.memory.benchmark_runs.values())
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        result = await self.session.execute(select(BenchmarkRun).offset(offset).limit(limit))
        items = [
            {
                "run_id": r.run_id,
                "status": r.status,
                "config": r.config,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
                "created_at": r.created_at,
            }
            for r in result.scalars().all()
        ]
        total = len((await self.session.execute(select(BenchmarkRun))).scalars().all())
        return items, total

    async def add_result(self, run_id: str, *, loss: float, method: str, metrics: dict[str, Any]) -> dict[str, Any]:
        now = utcnow()
        record = {
            "result_id": str(uuid.uuid4()),
            "run_id": run_id,
            "loss": loss,
            "method": method,
            "metrics": metrics,
            "data_class": "synthetic_benchmark",
            "created_at": now,
        }
        if self.memory:
            self.memory.benchmark_results.setdefault(run_id, []).append(record)
            return record

        assert self.session is not None
        self.session.add(
            BenchmarkResult(
                result_id=record["result_id"],
                run_id=run_id,
                loss=loss,
                method=method,
                metrics=metrics,
                data_class="synthetic_benchmark",
                created_at=now,
            )
        )
        await self.session.commit()
        return record

    async def list_results(self, run_id: str) -> list[dict[str, Any]]:
        if self.memory:
            return list(self.memory.benchmark_results.get(run_id, []))

        assert self.session is not None
        result = await self.session.execute(select(BenchmarkResult).where(BenchmarkResult.run_id == run_id))
        return [
            {
                "result_id": r.result_id,
                "run_id": r.run_id,
                "loss": r.loss,
                "method": r.method,
                "metrics": r.metrics,
                "data_class": r.data_class,
                "created_at": r.created_at,
            }
            for r in result.scalars().all()
        ]

    async def update_run_status(
        self,
        run_id: str,
        status: str,
        *,
        error_message: str | None = None,
    ) -> None:
        now = utcnow()
        if self.memory:
            run = self.memory.benchmark_runs.get(run_id)
            if run:
                run["status"] = status
                if status == "running":
                    run["started_at"] = now
                if status in ("completed", "failed"):
                    run["completed_at"] = now
                if error_message:
                    run["error_message"] = error_message
            return

        assert self.session is not None
        row = await self.session.get(BenchmarkRun, run_id)
        if not row:
            return
        row.status = status
        if status == "running":
            row.started_at = now
        if status in ("completed", "failed"):
            row.completed_at = now
        if error_message:
            row.error_message = error_message
        await self.session.commit()
