"""Multi-channel evidence fusion."""

from __future__ import annotations

import math
from dataclasses import dataclass

from cirda_core.config.channels import get_channel_profile
from cirda_core.config.constants import half_life_seconds
from cirda_core.domain.enums import EvidenceChannel


@dataclass(frozen=True, slots=True)
class ChannelObservation:
    """Observation count and age for a single channel."""

    channel: EvidenceChannel
    count: int
    age_seconds: float

    def __post_init__(self) -> None:
        if self.count < 0:
            raise ValueError("count must be non-negative")
        if self.age_seconds < 0:
            raise ValueError("age_seconds must be non-negative")


def channel_strength(observation: ChannelObservation) -> float:
    """
    Compute per-channel strength s_k at read time.

    s_k = r_k * (1 - exp(-n_k / tau_k)) * exp(-Δt / h_k)
    """
    profile = get_channel_profile(observation.channel)
    r_k = profile.reliability
    tau_k = profile.tau
    h_k = half_life_seconds(observation.channel)
    n_k = observation.count
    delta_t = observation.age_seconds

    if n_k == 0:
        return 0.0

    saturation = 1.0 - math.exp(-n_k / tau_k)
    decay = math.exp(-delta_t / h_k) if h_k > 0 else 0.0
    return r_k * saturation * decay


def fuse_channels(observations: list[ChannelObservation]) -> float:
    """
    Fuse multi-channel observations into combined strength S.

    S = 1 - Π_k (1 - s_k)
    """
    if not observations:
        return 0.0

    product = 1.0
    for obs in observations:
        s_k = channel_strength(obs)
        product *= 1.0 - s_k
    return 1.0 - product


def has_direct_evidence(observations: list[ChannelObservation]) -> bool:
    """Return True if any direct-class channel has observations."""
    from cirda_core.domain.enums import ChannelClass

    for obs in observations:
        if obs.count <= 0:
            continue
        profile = get_channel_profile(obs.channel)
        if profile.channel_class == ChannelClass.DIRECT:
            return True
    return False
