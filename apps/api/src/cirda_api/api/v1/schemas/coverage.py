"""Coverage schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from cirda_api.api.v1.schemas.common import ApiModel


class CoverageEstimate(ApiModel):
    coverage: float
    observed_entities: int
    total_entities: int
    suppressed_channels: list[str] = Field(default_factory=list)
    meets_threshold: bool
    c_min: float
    as_of: datetime | None = None


class CoverageSnapshotResponse(ApiModel):
    snapshot_id: str
    coverage: float
    observed_entities: int
    total_entities: int
    suppressed_channels: list[str] = Field(default_factory=list)
    scope: str | None = None
    captured_at: datetime
