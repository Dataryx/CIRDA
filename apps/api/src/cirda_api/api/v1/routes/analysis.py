"""Analysis endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from cirda_api.api.dependencies import ContainerDep
from cirda_api.security.rbac import RequireAnalyst


class BlastRadiusRequest(BaseModel):
    source_id: str
    as_of: datetime | None = None
    max_depth: int | None = None
    max_nodes: int | None = None


class ReachabilityRequest(BaseModel):
    source_id: str
    as_of: datetime | None = None
    max_depth: int | None = None


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/blast-radius")
async def blast_radius(body: BlastRadiusRequest, container: ContainerDep, _principal: RequireAnalyst) -> dict[str, object]:
    return await container.analysis_service.blast_radius(
        body.source_id,
        as_of=body.as_of,
        max_depth=body.max_depth,
        max_nodes=body.max_nodes,
    )


@router.post("/reachability")
async def reachability(body: ReachabilityRequest, container: ContainerDep, _principal: RequireAnalyst) -> dict[str, object]:
    return await container.analysis_service.reachability(body.source_id, as_of=body.as_of, max_depth=body.max_depth)


@router.get("/paths")
async def paths(
    source_id: str,
    container: ContainerDep,
    _principal: RequireAnalyst,
    as_of: datetime | None = Query(None),
    target_id: str | None = Query(None),
    max_depth: int = Query(8, ge=1, le=32),
    max_paths: int = Query(32, ge=1, le=100),
) -> dict[str, object]:
    return await container.analysis_service.critical_paths(
        source_id,
        target_id=target_id,
        as_of=as_of,
        max_depth=max_depth,
        max_paths=max_paths,
    )
