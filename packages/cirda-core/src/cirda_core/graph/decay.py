"""Evidence decay utilities (read-time only)."""

from __future__ import annotations

import math

from cirda_core.config.constants import half_life_seconds
from cirda_core.domain.enums import EvidenceChannel


def decay_factor(channel: EvidenceChannel, age_seconds: float) -> float:
    """
    Compute exp(-Δt / h_k) for a channel.

    Decay is applied at read/compute time; stored counters are never mutated.
    """
    if age_seconds < 0:
        raise ValueError("age_seconds must be non-negative")
    h_k = half_life_seconds(channel)
    if h_k <= 0:
        return 0.0
    return math.exp(-age_seconds / h_k)


def apply_decay_to_strength(strength: float, channel: EvidenceChannel, age_seconds: float) -> float:
    """Scale a base strength by temporal decay."""
    return strength * decay_factor(channel, age_seconds)
