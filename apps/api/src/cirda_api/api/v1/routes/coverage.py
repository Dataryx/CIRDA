"""Coverage endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.api.v1.schemas.coverage import CoverageEstimate, CoverageSnapshotResponse
from cirda_api.security.rbac import RequireViewer
from pydantic import BaseModel


class SnapshotListResponse(BaseModel):
    items: list[CoverageSnapshotResponse]
    page: PageMeta


router = APIRouter(prefix="/coverage", tags=["coverage"])


@router.get("", response_model=CoverageEstimate)
async def get_coverage(
    container: ContainerDep,
    _principal: RequireViewer,
    as_of: datetime | None = Query(None),
) -> CoverageEstimate:
    est = await container.coverage_service.estimate(as_of=as_of)
    return CoverageEstimate(**est)


@router.get("/snapshots", response_model=SnapshotListResponse)
async def list_snapshots(
    container: ContainerDep,
    _principal: RequireViewer,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> SnapshotListResponse:
    items, total = await container.coverage_service.list_snapshots(offset=offset, limit=limit)
    return SnapshotListResponse(
        items=[CoverageSnapshotResponse(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/channel-health")
async def channel_health(container: ContainerDep, _principal: RequireViewer) -> dict[str, object]:
    rows = await container.coverage_service.channel_health()
    return {"channels": rows}
