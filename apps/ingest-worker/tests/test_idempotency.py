"""Idempotency tests — INV-004 at-least-once with event_id deduplication."""

from __future__ import annotations

import pytest

from cirda_ingest.pipeline.stages import InboundMessage, sample_trace_raw


@pytest.mark.asyncio
async def test_duplicate_event_id_persisted_once(pipeline, memory_sink) -> None:
    raw = sample_trace_raw("evt-dup-1")
    msg1 = InboundMessage(raw=raw, message_id="m1", source="test")
    msg2 = InboundMessage(raw=raw, message_id="m2", source="test")

    r1 = await pipeline.process_batch([msg1])
    r2 = await pipeline.process_batch([msg2])

    assert r1.persist.created_event_ids == ["evt-dup-1"]
    assert r2.persist.deduped_event_ids == ["evt-dup-1"]
    assert len(memory_sink._memory.evidence) == 1  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_idempotency_key_dedupes_different_event_ids(pipeline, memory_sink) -> None:
    raw_a = sample_trace_raw("evt-a")
    raw_b = sample_trace_raw("evt-b")
    msg1 = InboundMessage(raw=raw_a, message_id="m1", source="test", idempotency_key="key-1")
    msg2 = InboundMessage(raw=raw_b, message_id="m2", source="test", idempotency_key="key-1")

    r1 = await pipeline.process_batch([msg1])
    r2 = await pipeline.process_batch([msg2])

    assert r1.persist.created_event_ids == ["evt-a"]
    assert r2.persist.deduped_event_ids == ["evt-a"]
    assert "evt-b" not in memory_sink._memory.evidence  # type: ignore[union-attr]
