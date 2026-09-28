"""Worker sink preserves operator necessity annotations."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Necessity, Relation
from cirda_core.domain.event import EvidenceEvent

from cirda_ingest.sinks.postgres_sink import PersistItem, PostgresSink


@pytest.mark.asyncio
async def test_upsert_preserves_operator_necessity(memory_sink: PostgresSink) -> None:
    now = datetime.now(timezone.utc)
    event = EvidenceEvent(
        event_id="nec-1",
        source_id="a",
        target_id="b",
        relation=Relation.CALLS,
        channel=EvidenceChannel.TRACE,
        observed_at=now,
    )
    edge = DependencyEdge(
        source_id="a",
        target_id="b",
        relation=Relation.CALLS,
        layer=GraphLayer.CONFIRMED,
        confidence=0.9,
        necessity=Necessity.OPTIONAL,
        evidence_count=1,
        last_observed_epoch=now.timestamp(),
    )
    await memory_sink.persist_batch([PersistItem(event=event, edge=edge, message_id="m1")])
    key = "a->b:calls"
    assert memory_sink._memory is not None
    assert memory_sink._memory.edges[key]["necessity"] == "optional"

    event2 = EvidenceEvent(
        event_id="nec-2",
        source_id="a",
        target_id="b",
        relation=Relation.CALLS,
        channel=EvidenceChannel.TRACE,
        observed_at=now,
    )
    edge2 = DependencyEdge(
        source_id="a",
        target_id="b",
        relation=Relation.CALLS,
        layer=GraphLayer.CONFIRMED,
        confidence=0.95,
        necessity=Necessity.UNKNOWN,
        evidence_count=2,
        last_observed_epoch=now.timestamp(),
    )
    await memory_sink.persist_batch([PersistItem(event=event2, edge=edge2, message_id="m2")])
    assert memory_sink._memory.edges[key]["necessity"] == "optional"
    assert memory_sink._memory.edges[key]["confidence"] == 0.95
