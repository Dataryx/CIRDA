"""Ingest schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from cirda_api.api.v1.schemas.common import ApiModel


class IngestEventRequest(ApiModel):
    raw: dict[str, Any]
    idempotency_key: str | None = None


class IngestBatchRequest(ApiModel):
    events: list[dict[str, Any]]
    idempotency_key: str | None = None


class EvidenceEventResponse(ApiModel):
    event_id: str
    source_id: str
    target_id: str
    relation: str
    channel: str
    observed_at: datetime
    source_type: str | None = None
    target_type: str | None = None
    payload_hash: str | None = None


class IngestResult(ApiModel):
    event: EvidenceEventResponse
    created: bool
    edge_updated: bool


class IngestBatchResult(ApiModel):
    results: list[IngestResult]
    accepted: int
    duplicates: int
