"""Candidate edge generation from evidence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.graph.layers import classify_layer
from cirda_core.inference.direction import translate_to_dependency_edge
from cirda_core.inference.fusion import ChannelObservation, fuse_channels, has_direct_evidence
from cirda_core.ports.clock import Clock


@dataclass(frozen=True, slots=True)
class CandidatePair:
    """Grouped observations for a source-target-relation triple."""

    actor_id: str
    counterpart_id: str
    relation: Relation
    channel_counts: dict[EvidenceChannel, int]
    last_observed: datetime


def group_events(events: list[EvidenceEvent]) -> dict[tuple[str, str, Relation], CandidatePair]:
    """Group evidence events by actor, counterpart, and relation."""
    groups: dict[tuple[str, str, Relation], CandidatePair] = {}
    for event in events:
        key = (event.source_id, event.target_id, event.relation)
        if key not in groups:
            groups[key] = CandidatePair(
                actor_id=event.source_id,
                counterpart_id=event.target_id,
                relation=event.relation,
                channel_counts={},
                last_observed=event.observed_at,
            )
        pair = groups[key]
        counts = dict(pair.channel_counts)
        counts[event.channel] = counts.get(event.channel, 0) + 1
        last = max(pair.last_observed, event.observed_at)
        groups[key] = CandidatePair(
            actor_id=pair.actor_id,
            counterpart_id=pair.counterpart_id,
            relation=pair.relation,
            channel_counts=counts,
            last_observed=last,
        )
    return groups


def generate_candidate_edge(
    pair: CandidatePair,
    clock: Clock,
    policy: PolicyConfig | None = None,
) -> DependencyEdge | None:
    """Generate a dependency edge from grouped observations."""
    cfg = policy or PolicyConfig()
    now = clock.now()
    # Clamp mild clock skew / future-dated telemetry to age 0 (fresh).
    age_seconds = max(0.0, (now - pair.last_observed).total_seconds())

    observations = [
        ChannelObservation(channel=ch, count=count, age_seconds=age_seconds)
        for ch, count in pair.channel_counts.items()
    ]
    confidence = fuse_channels(observations)
    layer = classify_layer(confidence, has_direct_evidence(observations), cfg)
    if layer is None:
        return None

    return translate_to_dependency_edge(
        actor_id=pair.actor_id,
        counterpart_id=pair.counterpart_id,
        relation=pair.relation,
        layer=layer,
        confidence=confidence,
        evidence_count=sum(pair.channel_counts.values()),
        last_observed_epoch=pair.last_observed.timestamp(),
    )


def generate_candidates(
    events: list[EvidenceEvent],
    clock: Clock,
    policy: PolicyConfig | None = None,
) -> list[DependencyEdge]:
    """Generate all candidate edges from evidence events."""
    groups = group_events(events)
    edges: list[DependencyEdge] = []
    for pair in groups.values():
        edge = generate_candidate_edge(pair, clock, policy)
        if edge is not None:
            edges.append(edge)
    return edges
