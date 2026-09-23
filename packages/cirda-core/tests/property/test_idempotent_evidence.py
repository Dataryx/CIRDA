"""Property: duplicate evidence does not decrease fused confidence."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from cirda_core.domain.enums import EvidenceChannel
from cirda_core.inference.fusion import ChannelObservation, fuse_channels


@given(
    count=st.integers(min_value=1, max_value=20),
    age=st.floats(min_value=0.0, max_value=86400.0, allow_nan=False),
)
@settings(max_examples=50)
def test_idempotent_evidence(count: int, age: float) -> None:
    single = fuse_channels([ChannelObservation(EvidenceChannel.TRACE, count, age)])
    duplicated = fuse_channels(
        [
            ChannelObservation(EvidenceChannel.TRACE, count, age),
            ChannelObservation(EvidenceChannel.TRACE, count, age),
        ]
    )
    assert duplicated >= single
