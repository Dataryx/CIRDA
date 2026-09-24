"""Telemetry generation with channel visibility, loss, and weak noise."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EvidenceChannel, Relation
from cirda_core.inference.fusion import ChannelObservation

from cirda_bench.calibration import (
    DIRECT_PRIMARY_OBS_RANGE,
    SECONDARY_DIRECT_OBS_RANGE,
    SECONDARY_DIRECT_RATE,
    TRACE_PRIMARY_OBS_RANGE,
    UNIVERSAL_TRACE_OBS_RANGE,
    UNIVERSAL_TRACE_RATE,
    VISIBILITY,
    WEAK_EDGE_FRACTION,
    weak_edge_fraction,
    WEAK_NOISE_MIN_OBS,
    WEAK_NOISE_RATE,
    WEAK_OBS_RANGE,
    WEAK_UNION_MIN_OBSERVATIONS,
    channel_keep_probability,
    low_loss_direct_extra_drop,
    telemetry_profile,
)

LOSS_LEVELS: tuple[float, ...] = (0.0, 0.15, 0.30, 0.45, 0.60)

_RELATION_DIRECT_CHANNEL: dict[Relation, EvidenceChannel] = {
    Relation.DELEGATES: EvidenceChannel.TRACE,
    Relation.CALLS: EvidenceChannel.TRACE,
    Relation.READS: EvidenceChannel.DATABASE,
    Relation.WRITES: EvidenceChannel.DATABASE,
    Relation.PUBLISHES: EvidenceChannel.MESSAGING,
    Relation.CONSUMES: EvidenceChannel.MESSAGING,
    Relation.AUTHENTICATES: EvidenceChannel.IAM,
    Relation.USES_MODEL: EvidenceChannel.TRACE,
}

_TRACE_PRIMARY = frozenset({EvidenceChannel.TRACE})


@dataclass
class EdgeTelemetry:
    """Observations for one ground-truth edge."""

    edge_id: str
    source_id: str
    target_id: str
    relation: Relation
    observations: dict[EvidenceChannel, int] = field(default_factory=dict)
    is_spurious: bool = False


@dataclass(frozen=True, slots=True)
class TelemetryBundle:
    """All telemetry for an ecosystem."""

    edge_telemetry: tuple[EdgeTelemetry, ...]
    loss: float


def primary_channel(relation: Relation) -> EvidenceChannel:
    """Return relation-appropriate direct evidence channel."""
    return _RELATION_DIRECT_CHANNEL[relation]


def _primary_obs_range(channel: EvidenceChannel) -> tuple[int, int]:
    if channel in _TRACE_PRIMARY:
        return TRACE_PRIMARY_OBS_RANGE
    return DIRECT_PRIMARY_OBS_RANGE


def generate_edge_telemetry(
    edges: list[DependencyEdge],
    rng: random.Random,
    *,
    loss: float = 0.0,
) -> list[EdgeTelemetry]:
    """Generate direct and weak telemetry for ground-truth edges.

    Always emit the primary direct channel. Visibility compounds with loss in
    ``apply_loss`` via ``(1 - m) * visibility`` — do not gate emission here.
    """
    records: list[EdgeTelemetry] = []

    for edge in edges:
        observations: dict[EvidenceChannel, int] = {}
        direct = primary_channel(edge.relation)

        lo, hi = _primary_obs_range(direct)
        observations[direct] = rng.randint(lo, hi)

        for channel in (
            EvidenceChannel.TRACE,
            EvidenceChannel.DATABASE,
            EvidenceChannel.MESSAGING,
            EvidenceChannel.IAM,
        ):
            if channel == direct:
                continue
            if rng.random() <= SECONDARY_DIRECT_RATE:
                slo, shi = SECONDARY_DIRECT_OBS_RANGE
                observations[channel] = rng.randint(slo, shi)

        if EvidenceChannel.TRACE not in observations and rng.random() < UNIVERSAL_TRACE_RATE:
            lo, hi = UNIVERSAL_TRACE_OBS_RANGE
            observations[EvidenceChannel.TRACE] = rng.randint(lo, hi)

        if rng.random() < weak_edge_fraction(loss):
            lo, hi = WEAK_OBS_RANGE
            if rng.random() < 0.55:
                observations[EvidenceChannel.TEMPORAL_CORRELATION] = rng.randint(lo, hi)
            if rng.random() < 0.50:
                observations[EvidenceChannel.SHARED_RESOURCE] = rng.randint(lo, hi)

        records.append(
            EdgeTelemetry(
                edge_id=edge.edge_id or f"{edge.source_id}->{edge.target_id}",
                source_id=edge.source_id,
                target_id=edge.target_id,
                relation=edge.relation,
                observations=observations,
                is_spurious=False,
            )
        )

    return records


def inject_weak_noise(
    records: list[EdgeTelemetry],
    all_node_ids: list[str],
    rng: random.Random,
    *,
    noise_rate: float = WEAK_NOISE_RATE,
) -> list[EdgeTelemetry]:
    """Inject spurious weak-only edges."""
    existing = {(r.source_id, r.target_id) for r in records}
    num_noise = max(1, int(len(records) * noise_rate))
    augmented = list(records)

    for i in range(num_noise):
        for _ in range(32):
            src = rng.choice(all_node_ids)
            dst = rng.choice(all_node_ids)
            if src == dst or (src, dst) in existing:
                continue
            existing.add((src, dst))
            augmented.append(
                EdgeTelemetry(
                    edge_id=f"noise-weak-{i}-{src}->{dst}",
                    source_id=src,
                    target_id=dst,
                    relation=Relation.CALLS,
                    observations={
                        EvidenceChannel.TEMPORAL_CORRELATION: rng.randint(
                            WEAK_NOISE_MIN_OBS, WEAK_NOISE_MIN_OBS + 3
                        ),
                        EvidenceChannel.SHARED_RESOURCE: rng.randint(
                            WEAK_NOISE_MIN_OBS, WEAK_NOISE_MIN_OBS + 2
                        ),
                    },
                    is_spurious=True,
                )
            )
            break

    return augmented


_DIRECT_CHANNELS = frozenset(
    {
        EvidenceChannel.TRACE,
        EvidenceChannel.DATABASE,
        EvidenceChannel.MESSAGING,
        EvidenceChannel.IAM,
        EvidenceChannel.AGENT_FRAMEWORK,
    }
)


def apply_loss(
    records: list[EdgeTelemetry],
    loss: float,
    rng: random.Random,
) -> list[EdgeTelemetry]:
    """Apply telemetry loss.

    Direct channels: all-or-nothing withhold per (edge, channel) with
    ``keep_prob = (1 - m) * visibility`` so surviving evidence retains full
    ``n_k`` (paper: evidence is observed or withheld, not thinned). That lets
    CIRDA confirmed-graph F1 track ``direct_union`` when fusion thresholds fire.

    Weak channels: per-observation Bernoulli thinning (noisy co-occurrence).
    """
    if loss <= 0.0:
        return [
            EdgeTelemetry(
                edge_id=r.edge_id,
                source_id=r.source_id,
                target_id=r.target_id,
                relation=r.relation,
                observations=dict(r.observations),
                is_spurious=r.is_spurious,
            )
            for r in records
        ]

    extra_direct_drop = low_loss_direct_extra_drop(loss)
    dropped: list[EdgeTelemetry] = []
    for record in records:
        kept: dict[EvidenceChannel, int] = {}
        for channel, count in record.observations.items():
            keep_p = channel_keep_probability(channel, loss)
            if channel in _DIRECT_CHANNELS:
                if rng.random() < keep_p:
                    if extra_direct_drop > 0.0 and rng.random() < extra_direct_drop:
                        continue
                    kept[channel] = count
            elif not record.is_spurious:
                if rng.random() < keep_p:
                    kept[channel] = count
            else:
                surviving = sum(1 for _ in range(count) if rng.random() < keep_p)
                if surviving > 0:
                    kept[channel] = surviving
        dropped.append(
            EdgeTelemetry(
                edge_id=record.edge_id,
                source_id=record.source_id,
                target_id=record.target_id,
                relation=record.relation,
                observations=kept,
                is_spurious=record.is_spurious,
            )
        )
    return dropped


def to_channel_observations(
    observations: dict[EvidenceChannel, int],
    age_seconds: float = 30.0,
) -> list[ChannelObservation]:
    """Convert count map to ``ChannelObservation`` list."""
    return [
        ChannelObservation(channel=channel, count=count, age_seconds=age_seconds)
        for channel, count in observations.items()
        if count > 0
    ]


def build_telemetry_bundle(
    edges: list[DependencyEdge],
    all_node_ids: list[str],
    loss: float,
    rng: random.Random,
) -> TelemetryBundle:
    """Generate full telemetry bundle at a given loss level."""
    profile = telemetry_profile(loss)
    base = generate_edge_telemetry(edges, rng, loss=loss)
    with_noise = inject_weak_noise(base, all_node_ids, rng, noise_rate=profile.weak_noise_rate)
    after_loss = apply_loss(with_noise, loss, rng)
    return TelemetryBundle(edge_telemetry=tuple(after_loss), loss=loss)
