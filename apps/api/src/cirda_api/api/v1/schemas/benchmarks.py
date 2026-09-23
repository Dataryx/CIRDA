"""Benchmark schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from cirda_api.api.v1.schemas.common import ApiModel, PageMeta


class BenchmarkRunCreate(ApiModel):
    config: dict[str, Any] = Field(default_factory=dict)


class BenchmarkRunResponse(ApiModel):
    run_id: str
    status: str
    config: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None


class BenchmarkResultResponse(ApiModel):
    result_id: str
    run_id: str
    loss: float
    method: str
    metrics: dict[str, Any]
    data_class: str = "synthetic_benchmark"
    created_at: datetime | None = None


class BenchmarkResultsEnvelope(ApiModel):
    run: BenchmarkRunResponse
    results: list[BenchmarkResultResponse]
    data_class: str = "synthetic_benchmark"
