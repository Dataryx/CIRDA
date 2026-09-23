"""Decay and retirement tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from cirda_core.domain.enums import ChangeType, EntityType, EvidenceChannel, GraphLayer, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.graph.decay import decay_factor
from cirda_core.graph.temporal_graph import TemporalGraph
from cirda_core.inference.candidate_generator import generate_candidate_edge, group_events
from cirda_core.inference.incremental import apply_events_incrementally
from cirda_core.analysis.change_types import applicable_change_types, requires_blast_recheck
from cirda_core.ports.clock import Clock


class AdvancingClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def now(self) -> datetime:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now = self._now + timedelta(seconds=seconds)


def _trace_event(event_id: str, src: str, tgt: str, at: datetime) -> EvidenceEvent:
    return EvidenceEvent(
        event_id=event_id,
        source_id=src,
        target_id=tgt,
        relation=Relation.CALLS,
        channel=EvidenceChannel.TRACE,
        observed_at=at,
    )


def test_decay_at_read_time_does_not_mutate_counts() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = AdvancingClock(base)
    events = [_trace_event(f"e{i}", "A", "B", base) for i in range(5)]
    groups = group_events(events)
    pair = next(iter(groups.values()))
    assert pair.channel_counts[EvidenceChannel.TRACE] == 5

    edge_fresh = generate_candidate_edge(pair, clock)
    clock.advance(86400 * 7)
    edge_stale = generate_candidate_edge(pair, clock)
    assert pair.channel_counts[EvidenceChannel.TRACE] == 5
    assert edge_fresh is not None and edge_stale is not None
    assert edge_stale.confidence < edge_fresh.confidence


def test_retirement_change_type() -> None:
    types = applicable_change_types(EntityType.AGENT)
    assert ChangeType.RETIREMENT in types
    assert requires_blast_recheck(ChangeType.RETIREMENT)


def test_decay_factor_half_life() -> None:
    h = 7 * 86400
    assert decay_factor(EvidenceChannel.TRACE, h) == pytest.approx(0.367879, abs=1e-4)


def test_incremental_graph_update() -> None:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = AdvancingClock(base)
    graph = TemporalGraph()
    events = [_trace_event("e1", "A", "B", base)]
    result = apply_events_incrementally(graph, events, clock)
    assert result.events_processed == 1
    assert len(result.added_edges) == 1
    assert graph.possible_edges or graph.confirmed_edges
