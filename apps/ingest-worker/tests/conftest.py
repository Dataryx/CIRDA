"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from cirda_core.config.policy import PolicyConfig

from cirda_ingest.pipeline.checkpoint import CheckpointManager, InMemoryCommitter
from cirda_ingest.pipeline.stages import IngestPipeline, sample_trace_raw
from cirda_ingest.sinks.metrics_sink import MetricsSink
from cirda_ingest.sinks.postgres_sink import PostgresSink


@pytest.fixture
def memory_sink() -> PostgresSink:
    return PostgresSink("sqlite+aiosqlite:///:memory:", memory_mode=True)


@pytest.fixture
def pipeline(memory_sink: PostgresSink) -> IngestPipeline:
    return IngestPipeline(
        memory_sink,
        policy=PolicyConfig(),
        metrics=MetricsSink(),
    )


@pytest.fixture
def checkpoint() -> CheckpointManager:
    return CheckpointManager(InMemoryCommitter())


@pytest.fixture
def trace_raw():
    return sample_trace_raw
