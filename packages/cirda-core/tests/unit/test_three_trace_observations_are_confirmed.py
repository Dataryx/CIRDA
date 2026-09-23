"""Three trace observations yield confirmed layer."""

from __future__ import annotations

from datetime import datetime, timezone

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.inference.candidate_generator import generate_candidates
from cirda_core.ports.clock import Clock


class FixedClock:
    def __init__(self) -> None:
        self._now = datetime(2026, 1, 15, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


def test_three_trace_observations_are_confirmed() -> None:
    clock: Clock = FixedClock()
    base = datetime(2026, 1, 15, tzinfo=timezone.utc)
    events = [
        EvidenceEvent(
            event_id=f"t{i}",
            source_id="A",
            target_id="B",
            relation=Relation.CALLS,
            channel=EvidenceChannel.TRACE,
            observed_at=base,
        )
        for i in range(3)
    ]
    edges = generate_candidates(events, clock, PolicyConfig())
    assert len(edges) == 1
    assert edges[0].layer == GraphLayer.CONFIRMED
