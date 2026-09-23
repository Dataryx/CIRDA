"""Pipeline stage unit tests."""

from __future__ import annotations

import pytest

from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import EntityType, EvidenceChannel
from cirda_core.resolution.entity_resolver import EntityResolver

from cirda_ingest.pipeline.dead_letter import PermanentIngestError
from cirda_ingest.pipeline.stages import InboundMessage, PipelineItem, sample_trace_raw


@pytest.mark.asyncio
async def test_normalize_stage_produces_event(pipeline) -> None:
    item = PipelineItem(
        message=InboundMessage(raw=sample_trace_raw("s1"), message_id="m1", source="test"),
        raw=sample_trace_raw("s1"),
    )
    pipeline._stage_normalize(item)
    assert item.event is not None
    assert item.event.event_id == "s1"
    assert item.event.channel == EvidenceChannel.TRACE


@pytest.mark.asyncio
async def test_normalize_invalid_payload_goes_to_permanent_error(pipeline) -> None:
    item = PipelineItem(
        message=InboundMessage(raw={"foo": "bar"}, message_id="m1", source="test"),
        raw={"foo": "bar"},
    )
    pipeline._stage_normalize(item)
    assert isinstance(item.permanent_error, PermanentIngestError)


@pytest.mark.asyncio
async def test_resolve_stage_maps_aliases(pipeline) -> None:
    resolver = EntityResolver()
    resolver.register(
        Entity(
            entity_id="canonical-a",
            entity_type=EntityType.SERVICE,
            name="A",
            aliases=frozenset(["alias-a"]),
        )
    )
    pipeline._resolver = resolver

    raw = sample_trace_raw("s2", source_id="alias-a", target_id="svc-b")
    item = PipelineItem(
        message=InboundMessage(raw=raw, message_id="m1", source="test"),
        raw=raw,
    )
    pipeline._stage_normalize(item)
    pipeline._stage_resolve(item)
    assert item.event is not None
    assert item.event.source_id == "canonical-a"


@pytest.mark.asyncio
async def test_fuse_stage_uses_incremental_counts_not_full_graph(pipeline, memory_sink) -> None:
    """R4: fusion reads per-pair counts from sink, not a rebuilt graph."""
    raw1 = sample_trace_raw("inc-1", source_id="x", target_id="y")
    raw2 = sample_trace_raw("inc-2", source_id="x", target_id="y")
    await pipeline.process_batch([
        InboundMessage(raw=raw1, message_id="m1", source="test"),
    ])
    count_before = await memory_sink.count_observations("x", "y", EvidenceChannel.TRACE)
    assert count_before == 1

    result = await pipeline.process_batch([
        InboundMessage(raw=raw2, message_id="m2", source="test"),
    ])
    assert result.persist.created_event_ids == ["inc-2"]
    count_after = await memory_sink.count_observations("x", "y", EvidenceChannel.TRACE)
    assert count_after == 2


@pytest.mark.asyncio
async def test_batch_marks_permanent_failures(pipeline) -> None:
    good = InboundMessage(raw=sample_trace_raw("good-1"), message_id="g1", source="test")
    bad = InboundMessage(raw={"invalid": True}, message_id="b1", source="test")
    result = await pipeline.process_batch([good, bad])
    assert result.persist.created_event_ids == ["good-1"]
    assert len(result.permanent_failures) == 1
