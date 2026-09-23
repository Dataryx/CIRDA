"""Normative constants for CIRDA inference and decision."""

from __future__ import annotations

from datetime import timedelta

from cirda_core.domain.enums import EvidenceChannel

THETA_C = 0.62
THETA_P = 0.28
C_MIN = 0.85

HALF_LIFE: dict[EvidenceChannel, timedelta] = {
    EvidenceChannel.TRACE: timedelta(days=7),
    EvidenceChannel.DATABASE: timedelta(days=14),
    EvidenceChannel.MESSAGING: timedelta(days=14),
    EvidenceChannel.IAM: timedelta(days=30),
    EvidenceChannel.AGENT_FRAMEWORK: timedelta(days=7),
    EvidenceChannel.TEMPORAL_CORRELATION: timedelta(days=3),
    EvidenceChannel.SHARED_RESOURCE: timedelta(days=7),
    EvidenceChannel.WORKFLOW_WINDOW: timedelta(days=3),
    EvidenceChannel.STATIC_DECLARED: timedelta(days=90),
}


def half_life_seconds(channel: EvidenceChannel) -> float:
    """Return half-life for a channel in seconds."""
    return HALF_LIFE[channel].total_seconds()
