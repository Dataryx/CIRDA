"""Future-dated telemetry is treated as age 0 (clock skew clamp)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.enums import EvidenceChannel, Relation
from cirda_core.inference.candidate_generator import CandidatePair, generate_candidate_edge


class _FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


def test_future_last_observed_clamps_age_and_still_emits_edge() -> None:
    now = datetime(2026, 9, 24, 12, 0, tzinfo=timezone.utc)
    future = now + timedelta(hours=2)
    pair = CandidatePair(
        actor_id="a",
        counterpart_id="b",
        relation=Relation.CALLS,
        channel_counts={EvidenceChannel.TRACE: 3},
        last_observed=future,
    )
    edge = generate_candidate_edge(pair, _FixedClock(now), PolicyConfig())
    assert edge is not None
    assert edge.confidence > 0.0
