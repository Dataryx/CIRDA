"""Intra-batch event_id dedupe and future-dated telemetry handling."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from cirda_ingest.pipeline.stages import InboundMessage, sample_trace_raw


@pytest.mark.asyncio
async def test_intra_batch_duplicate_event_ids_persist_once(pipeline, memory_sink) -> None:
    raw = sample_trace_raw("evt-batch-dup")
    msgs = [
        InboundMessage(raw=raw, message_id="m1", source="test"),
        InboundMessage(raw=raw, message_id="m2", source="test"),
        InboundMessage(raw=raw, message_id="m3", source="test"),
    ]
    result = await pipeline.process_batch(msgs)
    assert result.persist.created_event_ids == ["evt-batch-dup"]
    assert "m2" in result.persist.durable_message_ids
    assert "m3" in result.persist.durable_message_ids
    assert len(memory_sink._memory.evidence) == 1  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_future_observed_at_does_not_abort_batch(pipeline, memory_sink) -> None:
    future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    raw = sample_trace_raw("evt-future")
    raw["observed_at"] = future
    result = await pipeline.process_batch(
        [InboundMessage(raw=raw, message_id="m-future", source="test")]
    )
    assert result.permanent_failures == []
    assert result.persist.created_event_ids == ["evt-future"]
