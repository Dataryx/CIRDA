"""Shared API schemas."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VerdictSchema(StrEnum):
    UNSAFE = "UNSAFE"
    SAFE = "SAFE"
    INDETERMINATE = "INDETERMINATE"


class GraphLayerSchema(StrEnum):
    confirmed = "confirmed"
    possible = "possible"
    all = "all"


class EntityTypeSchema(StrEnum):
    agent = "agent"
    tool = "tool"
    service = "service"
    data = "data"
    queue = "queue"
    credential = "credential"
    model = "model"


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class HealthResponse(ApiModel):
    status: str = "ok"
    version: str


class ReadinessResponse(ApiModel):
    status: str
    database: str
    redis: str


class PageMeta(ApiModel):
    total: int
    offset: int
    limit: int
