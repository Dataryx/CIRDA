"""Entity endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import PageMeta
from cirda_api.api.v1.schemas.entities import EntityCreateRequest, EntityListResponse, EntityResponse
from cirda_api.security.rbac import RequireAnalyst, RequireViewer

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("", response_model=EntityListResponse)
async def list_entities(
    container: ContainerDep,
    _principal: RequireViewer,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    entity_type: str | None = None,
) -> EntityListResponse:
    items, total = await container.entity_service.list_entities(entity_type=entity_type, offset=offset, limit=limit)
    return EntityListResponse(
        items=[EntityResponse(**i) for i in items],
        page=PageMeta(total=total, offset=offset, limit=limit),
    )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str, container: ContainerDep, _principal: RequireViewer) -> EntityResponse:
    row = await container.entity_service.get_entity(entity_id)
    if not row:
        raise HTTPException(404, "Entity not found")
    return EntityResponse(**row)


@router.post("", response_model=EntityResponse, status_code=201)
async def create_entity(
    body: EntityCreateRequest,
    container: ContainerDep,
    principal: RequireAnalyst,
) -> EntityResponse:
    row = await container.entity_service.upsert_entity(
        entity_id=body.entity_id,
        entity_type=body.entity_type.value,
        name=body.name,
        criticality=body.criticality,
        metadata=body.metadata,
    )
    await container.audit_service.log(
        principal_id=principal.principal_id,
        action="entity.upsert",
        resource_type="entity",
        resource_id=body.entity_id,
    )
    return EntityResponse(**row)
