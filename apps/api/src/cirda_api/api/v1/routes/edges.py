"""Edge endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.security.rbac import RequireViewer
from pydantic import BaseModel


class EdgeResponse(BaseModel):
    edge_id: str
    source_id: str
    target_id: str
    relation: str
    layer: str
    confidence: float
    necessity: str = "unknown"
    evidence_count: int = 0


class EdgeListResponse(BaseModel):
    items: list[EdgeResponse]
    page: PageMeta


router = APIRouter(prefix="/edges", tags=["edges"])


@router.get("", response_model=EdgeListResponse)
async def list_edges(
    container: ContainerDep,
    _principal: RequireViewer,
    layer: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    as_of: datetime | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> EdgeListResponse:
    items, total = await container.edge_service.list_edges(
        layer=layer, source_id=source_id, target_id=target_id, as_of=as_of, offset=offset, limit=limit
    )
    return EdgeListResponse(
        items=[EdgeResponse(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/{edge_id}", response_model=EdgeResponse)
async def get_edge(
    edge_id: str,
    container: ContainerDep,
    _principal: RequireViewer,
    as_of: datetime | None = Query(None),
) -> EdgeResponse:
    row = await container.edge_service.get_edge(edge_id, as_of=as_of)
    if not row:
        raise HTTPException(404, "Edge not found")
    return EdgeResponse(**row)


@router.get("/{edge_id}/evidence")
async def edge_evidence(edge_id: str, container: ContainerDep, _principal: RequireViewer) -> dict[str, object]:
    events = await container.edge_service.edge_evidence(edge_id)
    return {"edge_id": edge_id, "events": events}
