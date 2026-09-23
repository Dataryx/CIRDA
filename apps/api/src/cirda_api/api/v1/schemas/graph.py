"""Graph payload schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from cirda_api.api.v1.schemas.common import ApiModel, GraphLayerSchema


class GraphNode(ApiModel):
    entity_id: str
    entity_type: str
    name: str
    criticality: str


class GraphEdge(ApiModel):
    edge_id: str
    source_id: str
    target_id: str
    relation: str
    layer: str
    confidence: float
    necessity: str = "unknown"
    evidence_count: int = 0


class GraphPayload(ApiModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    layer: GraphLayerSchema | str
    as_of: datetime | None = None
    engine_version: str
