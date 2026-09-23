"""Weak channels alone cannot confirm."""

from __future__ import annotations

from datetime import datetime, timezone

from cirda_core.config.constants import THETA_C
from cirda_core.domain.enums import EvidenceChannel, GraphLayer
from cirda_core.inference.fusion import ChannelObservation, fuse_channels
from cirda_core.inference.weak_signals import can_confirm_layer, classify_with_weak_guard


def test_weak_channels_alone_cannot_confirm() -> None:
    observations = [
        ChannelObservation(EvidenceChannel.TEMPORAL_CORRELATION, count=100, age_seconds=0.0),
        ChannelObservation(EvidenceChannel.SHARED_RESOURCE, count=100, age_seconds=0.0),
    ]
    assert can_confirm_layer(observations) is False
    fused = fuse_channels(observations)
    assert fused >= THETA_C
    layer = classify_with_weak_guard(observations, THETA_C, 0.28)
    assert layer == GraphLayer.POSSIBLE
    assert layer != GraphLayer.CONFIRMED
