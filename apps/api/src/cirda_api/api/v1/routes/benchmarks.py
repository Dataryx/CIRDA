"""Benchmark endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.benchmarks import (
    BenchmarkResultResponse,
    BenchmarkResultsEnvelope,
    BenchmarkRunCreate,
    BenchmarkRunResponse,
)
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.security.rbac import RequireAdmin, RequireViewer
from pydantic import BaseModel


class BenchmarkRunListResponse(BaseModel):
    items: list[BenchmarkRunResponse]
    page: PageMeta


router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("/runs", response_model=BenchmarkRunListResponse)
async def list_runs(
    container: ContainerDep,
    _principal: RequireViewer,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> BenchmarkRunListResponse:
    items, total = await container.benchmark_service.list_runs(offset=offset, limit=limit)
    return BenchmarkRunListResponse(
        items=[BenchmarkRunResponse(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )


@router.post("/runs", response_model=BenchmarkRunResponse, status_code=201)
async def create_run(
    body: BenchmarkRunCreate,
    container: ContainerDep,
    principal: RequireAdmin,
) -> BenchmarkRunResponse:
    run = await container.benchmark_service.create_run(body.config)
    if body.config.get("seed_demo"):
        await container.benchmark_service.seed_demo_results(run["run_id"])
        run = await container.benchmark_service.get_run(run["run_id"]) or run
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="benchmark.create",
        resource_type="benchmark_run",
        resource_id=run["run_id"],
    )
    return BenchmarkRunResponse(**run)


@router.get("/runs/{run_id}", response_model=BenchmarkResultsEnvelope)
async def get_run_results(run_id: str, container: ContainerDep, _principal: RequireViewer) -> BenchmarkResultsEnvelope:
    run = await container.benchmark_service.get_run(run_id)
    if not run:
        raise HTTPException(404, "Benchmark run not found")
    results = await container.benchmark_service.get_results(run_id)
    return BenchmarkResultsEnvelope(
        run=BenchmarkRunResponse(**run),
        results=[BenchmarkResultResponse(**r) for r in results],
        data_class="synthetic_benchmark",
    )
