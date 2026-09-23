"""Entity schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from cirda_api.api.v1.schemas.common import ApiModel, EntityTypeSchema, PageMeta


class EntityResponse(ApiModel):
    entity_id: str
    entity_type: EntityTypeSchema | str
    name: str
    criticality: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)
    aliases: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EntityCreateRequest(ApiModel):
    entity_id: str
    entity_type: EntityTypeSchema
    name: str
    criticality: str = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class EntityListResponse(ApiModel):
    items: list[EntityResponse]
    page: PageMeta
