"""Static declared channels can confirm edges."""

from __future__ import annotations

from cirda_core.config.constants import THETA_C, THETA_P
from cirda_core.domain.enums import EvidenceChannel, GraphLayer
from cirda_core.graph.layers import classify_layer
from cirda_core.inference.fusion import (
    ChannelObservation,
    fuse_channels,
    has_confirming_evidence,
    has_direct_evidence,
)
from cirda_core.inference.weak_signals import can_confirm_layer, classify_with_weak_guard


def test_static_declared_alone_can_confirm() -> None:
    observations = [
        ChannelObservation(EvidenceChannel.STATIC_DECLARED, count=5, age_seconds=0.0),
    ]
    assert has_direct_evidence(observations) is False
    assert has_confirming_evidence(observations) is True
    assert can_confirm_layer(observations) is True
    fused = fuse_channels(observations)
    assert fused >= THETA_C
    layer = classify_layer(fused, has_confirming_evidence(observations))
    assert layer == GraphLayer.CONFIRMED
    assert classify_with_weak_guard(observations, THETA_C, THETA_P) == GraphLayer.CONFIRMED
