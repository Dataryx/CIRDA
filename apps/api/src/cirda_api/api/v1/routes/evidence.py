"""Evidence query endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.api.v1.schemas.ingest import EvidenceEventResponse
from cirda_api.security.rbac import RequireViewer
from pydantic import BaseModel


class EvidenceListResponse(BaseModel):
    items: list[EvidenceEventResponse]
    page: PageMeta


router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("", response_model=EvidenceListResponse)
async def list_evidence(
    container: ContainerDep,
    _principal: RequireViewer,
    source_id: str | None = None,
    target_id: str | None = None,
    channel: str | None = None,
    as_of: datetime | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
) -> EvidenceListResponse:
    items, total = await container.evidence_service.list_events(
        source_id=source_id,
        target_id=target_id,
        channel=channel,
        as_of=as_of,
        offset=offset,
        limit=limit,
    )
    return EvidenceListResponse(
        items=[EvidenceEventResponse(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/{event_id}", response_model=EvidenceEventResponse)
async def get_evidence(event_id: str, container: ContainerDep, _principal: RequireViewer) -> EvidenceEventResponse:
    row = await container.evidence_service.get_event(event_id)
    if not row:
        raise HTTPException(404, "Evidence event not found")
    return EvidenceEventResponse(**row)
