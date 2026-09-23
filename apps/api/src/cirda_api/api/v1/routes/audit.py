"""Audit log endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.security.rbac import RequireAdmin
from pydantic import BaseModel


class AuditEntry(BaseModel):
    log_id: str
    principal_id: str | None
    action: str
    resource_type: str
    resource_id: str | None = None
    details: dict[str, object] = {}
    created_at: object


class AuditListResponse(BaseModel):
    items: list[AuditEntry]
    page: PageMeta


router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=AuditListResponse)
async def list_audit(
    container: ContainerDep,
    _principal: RequireAdmin,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> AuditListResponse:
    items, total = await container.audit_service.list_entries(offset=offset, limit=limit)
    return AuditListResponse(
        items=[AuditEntry(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )
