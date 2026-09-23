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

WEAK_EDGE_FRACTION = 0.55
WEAK_OBS_RANGE = (6, 10)
WEAK_NOISE_RATE = 0.008

TRACE_PHANTOM_RATE_BY_LOSS: dict[float, float] = {
    0.30: 0.12,
    0.45: 0.10,
    0.60: 0.085,
}
TRACE_MIN_OBSERVATIONS = 1
TRACE_METHOD_EXTRA_DROP: dict[float, float] = {
    0.30: 0.05,
    0.45: 0.045,
    0.60: 0.04,
}
TRACE_CRITICAL_PATH_DROP: dict[float, float] = {
    0.30: 0.82,
    0.45: 0.78,
    0.60: 0.72,
}

WEAK_NOISE_MIN_OBS = 3
WEAK_UNION_MIN_OBSERVATIONS = 8


@dataclass(frozen=True, slots=True)
class TelemetryProfile:
    loss: float
    weak_noise_rate: float


def telemetry_profile(loss: float) -> TelemetryProfile:
    return TelemetryProfile(
        loss=loss,
        weak_noise_rate=WEAK_NOISE_RATE * (1.0 + loss * 0.12),
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
