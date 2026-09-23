"""Graph endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.graph import GraphPayload
from cirda_core.domain.enums import GraphLayer
from cirda_api.security.rbac import RequireViewer

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("", response_model=GraphPayload)
async def get_graph(
    container: ContainerDep,
    _principal: RequireViewer,
    layer: str | None = Query(None),
    as_of: datetime | None = Query(None),
) -> GraphPayload:
    layer_enum = GraphLayer(layer) if layer in ("confirmed", "possible") else None
    payload = await container.graph_service.get_graph_payload(layer=layer_enum, as_of=as_of)
    return GraphPayload(**payload)
