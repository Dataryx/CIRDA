"""Ingest endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Header

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.ingest import (
    IngestBatchRequest,
    IngestBatchResult,
    IngestEventRequest,
    IngestResult,
)
from cirda_api.observability.metrics import INGEST_EVENTS
from cirda_api.security.rbac import RequireAnalyst

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/events", response_model=IngestResult)
async def ingest_event(
    body: IngestEventRequest,
    container: ContainerDep,
    _principal: RequireAnalyst,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> IngestResult:
    key = body.idempotency_key or idempotency_key
    result = await container.ingest_service.ingest_raw(body.raw, idempotency_key=key)
    INGEST_EVENTS.labels(created=str(result["created"]).lower()).inc()
    await container.audit_service.log(
        principal_id=_principal.principal_id,
        action="ingest.event",
        resource_type="evidence",
        resource_id=result["event"]["event_id"],
    )
    return IngestResult(**result)


@router.post("/events/batch", response_model=IngestBatchResult)
async def ingest_batch(
    body: IngestBatchRequest,
    container: ContainerDep,
    _principal: RequireAnalyst,
) -> IngestBatchResult:
    results: list[IngestResult] = []
    duplicates = 0
    for raw in body.events:
        r = await container.ingest_service.ingest_raw(raw, idempotency_key=body.idempotency_key)
        if not r["created"]:
            duplicates += 1
        results.append(IngestResult(**r))
    return IngestBatchResult(results=results, accepted=len(results) - duplicates, duplicates=duplicates)
