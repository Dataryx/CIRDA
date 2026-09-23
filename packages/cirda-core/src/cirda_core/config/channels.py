"""Evidence channel profiles."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from cirda_core.config.constants import HALF_LIFE
from cirda_core.domain.enums import ChannelClass, EvidenceChannel


@dataclass(frozen=True, slots=True)
class ChannelProfile:
    """Reliability and decay parameters for an evidence channel."""

    channel: EvidenceChannel
    channel_class: ChannelClass
    reliability: float
    tau: float
    half_life: timedelta
    normative: bool = False


CHANNEL_PROFILES: dict[EvidenceChannel, ChannelProfile] = {
    EvidenceChannel.TRACE: ChannelProfile(
        channel=EvidenceChannel.TRACE,
        channel_class=ChannelClass.DIRECT,
        reliability=0.995,
        tau=3.0,
        half_life=HALF_LIFE[EvidenceChannel.TRACE],
        normative=True,
    ),
    EvidenceChannel.DATABASE: ChannelProfile(
        channel=EvidenceChannel.DATABASE,
        channel_class=ChannelClass.DIRECT,
        reliability=0.985,
        tau=3.0,
        half_life=HALF_LIFE[EvidenceChannel.DATABASE],
        normative=True,
    ),
    EvidenceChannel.MESSAGING: ChannelProfile(
        channel=EvidenceChannel.MESSAGING,
        channel_class=ChannelClass.DIRECT,
        reliability=0.990,
        tau=3.0,
        half_life=HALF_LIFE[EvidenceChannel.MESSAGING],
        normative=True,
    ),
    EvidenceChannel.IAM: ChannelProfile(
        channel=EvidenceChannel.IAM,
        channel_class=ChannelClass.DIRECT,
        reliability=0.990,
        tau=2.0,
        half_life=HALF_LIFE[EvidenceChannel.IAM],
        normative=True,
    ),
    EvidenceChannel.AGENT_FRAMEWORK: ChannelProfile(
        channel=EvidenceChannel.AGENT_FRAMEWORK,
        channel_class=ChannelClass.DIRECT,
        reliability=0.980,
        tau=3.0,
        half_life=HALF_LIFE[EvidenceChannel.AGENT_FRAMEWORK],
    ),
    EvidenceChannel.TEMPORAL_CORRELATION: ChannelProfile(
        channel=EvidenceChannel.TEMPORAL_CORRELATION,
        channel_class=ChannelClass.WEAK,
        reliability=0.380,
        tau=12.0,
        half_life=HALF_LIFE[EvidenceChannel.TEMPORAL_CORRELATION],
        normative=True,
    ),
    EvidenceChannel.SHARED_RESOURCE: ChannelProfile(
        channel=EvidenceChannel.SHARED_RESOURCE,
        channel_class=ChannelClass.WEAK,
        reliability=0.500,
        tau=8.0,
        half_life=HALF_LIFE[EvidenceChannel.SHARED_RESOURCE],
        normative=True,
    ),
    EvidenceChannel.WORKFLOW_WINDOW: ChannelProfile(
        channel=EvidenceChannel.WORKFLOW_WINDOW,
        channel_class=ChannelClass.WEAK,
        reliability=0.450,
        tau=10.0,
        half_life=HALF_LIFE[EvidenceChannel.WORKFLOW_WINDOW],
    ),
    EvidenceChannel.STATIC_DECLARED: ChannelProfile(
        channel=EvidenceChannel.STATIC_DECLARED,
        channel_class=ChannelClass.DECLARED,
        reliability=0.900,
        tau=1.0,
        half_life=HALF_LIFE[EvidenceChannel.STATIC_DECLARED],
    ),
}


def get_channel_profile(channel: EvidenceChannel) -> ChannelProfile:
    """Return the profile for a channel."""
    return CHANNEL_PROFILES[channel]
