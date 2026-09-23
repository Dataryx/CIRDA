"""Property: fusion is monotonic in count and anti-monotonic in age."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from cirda_core.domain.enums import EvidenceChannel
from cirda_core.inference.fusion import ChannelObservation, channel_strength, fuse_channels


@given(
    n1=st.integers(min_value=0, max_value=50),
    n2=st.integers(min_value=0, max_value=50),
    age=st.floats(min_value=0.0, max_value=1e6, allow_nan=False),
)
@settings(max_examples=100)
def test_count_monotonicity(n1: int, n2: int, age: float) -> None:
    if n1 <= n2:
        s1 = channel_strength(ChannelObservation(EvidenceChannel.TRACE, n1, age))
        s2 = channel_strength(ChannelObservation(EvidenceChannel.TRACE, n2, age))
        assert s2 >= s1


@given(
    age1=st.floats(min_value=0.0, max_value=1e5, allow_nan=False),
    age2=st.floats(min_value=0.0, max_value=1e5, allow_nan=False),
    count=st.integers(min_value=1, max_value=20),
)
@settings(max_examples=100)
def test_age_anti_monotonicity(age1: float, age2: float, count: int) -> None:
    if age1 <= age2:
        s1 = channel_strength(ChannelObservation(EvidenceChannel.DATABASE, count, age1))
        s2 = channel_strength(ChannelObservation(EvidenceChannel.DATABASE, count, age2))
        assert s1 >= s2


@given(
    counts=st.lists(st.integers(min_value=1, max_value=10), min_size=1, max_size=3),
)
@settings(max_examples=50)
def test_multi_channel_monotonicity(counts: list[int]) -> None:
    obs = [
        ChannelObservation(EvidenceChannel.TRACE, counts[0], 0.0),
    ]
    fused_single = fuse_channels(obs)
    if len(counts) > 1:
        obs.append(ChannelObservation(EvidenceChannel.DATABASE, counts[1], 0.0))
    fused_multi = fuse_channels(obs)
    assert fused_multi >= fused_single
