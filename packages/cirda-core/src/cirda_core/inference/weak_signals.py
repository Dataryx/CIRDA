"""Weak signal handling."""

from __future__ import annotations

from cirda_core.config.channels import CHANNEL_PROFILES
from cirda_core.domain.enums import ChannelClass, EvidenceChannel, GraphLayer
from cirda_core.inference.fusion import ChannelObservation, fuse_channels


def is_weak_channel(channel: EvidenceChannel) -> bool:
    """Return True if channel is weak class."""
    return CHANNEL_PROFILES[channel].channel_class == ChannelClass.WEAK


def weak_only_observations(observations: list[ChannelObservation]) -> bool:
    """Return True if all non-zero observations are from weak channels."""
    active = [o for o in observations if o.count > 0]
    if not active:
        return False
    return all(is_weak_channel(o.channel) for o in active)


def can_confirm_layer(observations: list[ChannelObservation]) -> bool:
    """
    Determine if observations can support confirmed layer.

    Weak channels alone cannot confirm.
    """
    if weak_only_observations(observations):
        return False
    from cirda_core.inference.fusion import has_direct_evidence

    return has_direct_evidence(observations)


def max_weak_fused_confidence(observations: list[ChannelObservation]) -> float:
    """Return fused confidence when only weak channels contribute."""
    weak_obs = [o for o in observations if is_weak_channel(o.channel) and o.count > 0]
    return fuse_channels(weak_obs)


def classify_with_weak_guard(
    observations: list[ChannelObservation],
    theta_confirmed: float,
    theta_possible: float,
) -> GraphLayer | None:
    """Classify layer respecting weak-channel confirmation guard."""
    confidence = fuse_channels(observations)
    if confidence < theta_possible:
        return None
    if confidence >= theta_confirmed and can_confirm_layer(observations):
        return GraphLayer.CONFIRMED
    return GraphLayer.POSSIBLE
