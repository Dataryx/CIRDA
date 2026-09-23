"""Fusion equation tests."""

from __future__ import annotations

import math

import pytest

from cirda_core.domain.enums import EvidenceChannel
from cirda_core.inference.fusion import ChannelObservation, channel_strength, fuse_channels


def test_diminishing_returns() -> None:
    obs1 = ChannelObservation(EvidenceChannel.TRACE, count=1, age_seconds=0.0)
    obs5 = ChannelObservation(EvidenceChannel.TRACE, count=5, age_seconds=0.0)
    s1 = channel_strength(obs1)
    s5 = channel_strength(obs5)
    assert s5 > s1
    marginal = channel_strength(ChannelObservation(EvidenceChannel.TRACE, count=10, age_seconds=0.0)) - s5
    earlier_marginal = s5 - s1
    assert marginal < earlier_marginal


def test_stale_decay() -> None:
    fresh = channel_strength(ChannelObservation(EvidenceChannel.DATABASE, count=10, age_seconds=0.0))
    stale = channel_strength(ChannelObservation(EvidenceChannel.DATABASE, count=10, age_seconds=86400.0))
    assert stale < fresh


def test_multi_channel_increase() -> None:
    single = fuse_channels([ChannelObservation(EvidenceChannel.DATABASE, count=5, age_seconds=0.0)])
    multi = fuse_channels(
        [
            ChannelObservation(EvidenceChannel.DATABASE, count=5, age_seconds=0.0),
            ChannelObservation(EvidenceChannel.TRACE, count=5, age_seconds=0.0),
        ]
    )
    assert multi > single


def test_published_fixture_database_temporal_fuse() -> None:
    db = channel_strength(ChannelObservation(EvidenceChannel.DATABASE, count=14, age_seconds=3600.0))
    temporal = channel_strength(
        ChannelObservation(EvidenceChannel.TEMPORAL_CORRELATION, count=21, age_seconds=1800.0)
    )
    assert db == pytest.approx(0.97284, abs=1e-4)
    assert temporal == pytest.approx(0.31179, abs=1e-4)
    fused = fuse_channels(
        [
            ChannelObservation(EvidenceChannel.DATABASE, count=14, age_seconds=3600.0),
            ChannelObservation(EvidenceChannel.TEMPORAL_CORRELATION, count=21, age_seconds=1800.0),
        ]
    )
    expected = 1.0 - (1.0 - db) * (1.0 - temporal)
    assert fused == pytest.approx(0.98131, abs=1e-4)
    assert fused == pytest.approx(expected, abs=1e-6)


def test_zero_count_yields_zero_strength() -> None:
    assert channel_strength(ChannelObservation(EvidenceChannel.TRACE, count=0, age_seconds=0.0)) == 0.0


def test_fusion_formula_structure() -> None:
    obs = ChannelObservation(EvidenceChannel.TRACE, count=3, age_seconds=100.0)
    profile_r = 0.995
    profile_tau = 3.0
    h_k = 7 * 86400
    expected = profile_r * (1 - math.exp(-3 / profile_tau)) * math.exp(-100 / h_k)
    assert channel_strength(obs) == pytest.approx(expected, rel=1e-9)
