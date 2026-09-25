"""EventBatcher same-task flush behavior (Kafka-safe)."""

from __future__ import annotations

import pytest

from cirda_ingest.pipeline.batcher import EventBatcher
from cirda_ingest.pipeline.stages import InboundMessage, sample_trace_raw


@pytest.mark.asyncio
async def test_batcher_flushes_on_max_events() -> None:
    flushed: list[list[InboundMessage]] = []

    async def handler(batch: list[InboundMessage]) -> None:
        flushed.append(batch)

    batcher = EventBatcher(handler, max_events=3, max_wait_seconds=10.0)
    for i in range(3):
        await batcher.add(
            InboundMessage(raw=sample_trace_raw(f"e{i}"), message_id=f"m{i}", source="test")
        )
    assert len(flushed) == 1
    assert len(flushed[0]) == 3


@pytest.mark.asyncio
async def test_batcher_flush_if_due_respects_window() -> None:
    flushed: list[int] = []

    async def handler(batch: list[InboundMessage]) -> None:
        flushed.append(len(batch))

    batcher = EventBatcher(handler, max_events=50, max_wait_seconds=0.0)
    await batcher.add(InboundMessage(raw=sample_trace_raw("e1"), message_id="m1", source="test"))
    await batcher.flush_if_due()
    assert flushed == [1]


@pytest.mark.asyncio
async def test_batcher_does_not_schedule_background_tasks() -> None:
    """Regression: background flush tasks raced aiokafka commit."""
    calls = 0

    async def handler(batch: list[InboundMessage]) -> None:
        nonlocal calls
        calls += 1

    batcher = EventBatcher(handler, max_events=10, max_wait_seconds=60.0)
    await batcher.add(InboundMessage(raw=sample_trace_raw("e1"), message_id="m1", source="test"))
    assert not hasattr(batcher, "_flush_task") or getattr(batcher, "_flush_task", None) is None
    assert calls == 0
    await batcher.flush()
    assert calls == 1
