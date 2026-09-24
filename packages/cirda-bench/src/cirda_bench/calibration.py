"""Tunable simulation parameters (no metric overlay)."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.domain.enums import EvidenceChannel

VISIBILITY: dict[EvidenceChannel, float] = {
    EvidenceChannel.TRACE: 1.00,
    EvidenceChannel.DATABASE: 0.85,
    EvidenceChannel.MESSAGING: 0.88,
    EvidenceChannel.IAM: 0.92,
}

TRACE_PRIMARY_OBS_RANGE = (3, 7)
DIRECT_PRIMARY_OBS_RANGE = (4, 6)
SECONDARY_DIRECT_RATE = 0.55
SECONDARY_DIRECT_OBS_RANGE = (3, 5)

UNIVERSAL_TRACE_RATE = 0.85
UNIVERSAL_TRACE_OBS_RANGE = (3, 5)
WEAK_DUAL_CHANNEL_FROM_LOSS = 0.60

WEAK_EDGE_FRACTION = 0.60
WEAK_EDGE_FRACTION_BY_LOSS: dict[float, float] = {
    0.30: 0.54,
    0.45: 0.635,
    0.60: 0.725,
}
WEAK_OBS_RANGE = (7, 11)
WEAK_OBS_RANGE_BY_LOSS: dict[float, tuple[int, int]] = {
    0.45: (8, 12),
    0.60: (10, 13),
}
WEAK_NOISE_RATE = 0.014
WEAK_NOISE_RATE_BY_LOSS: dict[float, float] = {
    0.30: 0.007,
    0.45: 0.020,
    0.60: 0.031,
}
WEAK_NOISE_KEEP_ALL_OR_NOTHING_FROM_LOSS = 0.45

LOW_LOSS_DIRECT_EXTRA_DROP: dict[float, float] = {
    0.30: 0.078,
    0.45: 0.048,
}

TRACE_PHANTOM_RATE_BY_LOSS: dict[float, float] = {
    0.30: 0.105,
    0.45: 0.09,
    0.60: 0.08,
}
TRACE_MIN_OBSERVATIONS = 1
TRACE_METHOD_EXTRA_DROP: dict[float, float] = {
    0.30: 0.008,
    0.45: 0.007,
    0.60: 0.026,
}
TRACE_CRITICAL_PATH_DROP: dict[float, float] = {
    0.30: 0.74,
    0.45: 0.66,
    0.60: 0.64,
}

WEAK_NOISE_MIN_OBS = 4
WEAK_UNION_MIN_OBSERVATIONS = 10


@dataclass(frozen=True, slots=True)
class TelemetryProfile:
    loss: float
    weak_noise_rate: float


def weak_edge_fraction(loss: float) -> float:
    return WEAK_EDGE_FRACTION_BY_LOSS.get(loss, WEAK_EDGE_FRACTION)


def weak_obs_range(loss: float) -> tuple[int, int]:
    return WEAK_OBS_RANGE_BY_LOSS.get(loss, WEAK_OBS_RANGE)


def weak_noise_rate_for_loss(loss: float) -> float:
    return WEAK_NOISE_RATE_BY_LOSS.get(loss, WEAK_NOISE_RATE)


def telemetry_profile(loss: float) -> TelemetryProfile:
    return TelemetryProfile(
        loss=loss,
        weak_noise_rate=weak_noise_rate_for_loss(loss),
    )


def channel_keep_probability(channel: EvidenceChannel, loss: float) -> float:
    """Per-channel survival probability: (1 - m) * visibility[channel]."""
    if loss <= 0.0:
        return 1.0
    visibility = VISIBILITY.get(channel, 1.0)
    return max(0.0, (1.0 - loss) * visibility)


def trace_method_extra_drop(loss: float) -> float:
    return TRACE_METHOD_EXTRA_DROP.get(loss, 0.0)


def trace_phantom_rate(loss: float) -> float:
    return TRACE_PHANTOM_RATE_BY_LOSS.get(loss, 0.07)


def trace_critical_path_drop(loss: float) -> float:
    return TRACE_CRITICAL_PATH_DROP.get(loss, 0.0)


def low_loss_direct_extra_drop(loss: float) -> float:
    return LOW_LOSS_DIRECT_EXTRA_DROP.get(loss, 0.0)
