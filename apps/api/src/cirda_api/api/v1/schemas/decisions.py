"""Decision report schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from cirda_api.api.v1.schemas.common import ApiModel, VerdictSchema


class RunbookActionSchema(ApiModel):
    stage: str
    description: str
    entity_id: str | None = None


class ProbePlanSchema(ApiModel):
    entity_id: str
    channels: list[str] = Field(default_factory=list)
    rationale: str


class DecisionRationale(ApiModel):
    summary: str
    details: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    blast_radius: dict[str, Any] = Field(default_factory=dict)
    coverage_breakdown: dict[str, Any] = Field(default_factory=dict)
    suggested_runbook: list[RunbookActionSchema] = Field(default_factory=list)
    suggested_probes: list[ProbePlanSchema] = Field(default_factory=list)


class DecisionReport(ApiModel):
    decision_id: str
    entity_id: str
    verdict: VerdictSchema
    coverage: float
    truncated: bool = False
    reason_codes: list[str] = Field(default_factory=list)
    rationale: DecisionRationale | dict[str, Any]
    limitations_footer: str
    as_of: datetime
    engine_version: str
    change_type: str | None = None
    supersedes: str | None = None
    superseded_by: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    paths: list[dict[str, Any]] = Field(default_factory=list)


class DecisionEvaluateRequest(ApiModel):
    entity_id: str
    as_of: datetime | None = None
    change_type: str | None = None
