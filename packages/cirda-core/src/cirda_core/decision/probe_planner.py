"""Probe planning for INDETERMINATE coverage gaps (feature-flagged)."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.config.channels import CHANNEL_PROFILES
from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.enums import ChannelClass, EvidenceChannel

_CHANNEL_RATIONALE: dict[EvidenceChannel, str] = {
    EvidenceChannel.TRACE: "Restore or expand distributed tracing for this entity's call paths.",
    EvidenceChannel.DATABASE: "Restore database audit/collector coverage for this entity's data dependencies.",
    EvidenceChannel.MESSAGING: "Restore messaging bus telemetry for this entity's publish/consume edges.",
    EvidenceChannel.IAM: "Restore IAM/authz event coverage for this entity's identity bindings.",
    EvidenceChannel.AGENT_FRAMEWORK: "Enable agent-framework instrumentation for tool and delegation edges.",
    EvidenceChannel.TEMPORAL_CORRELATION: "Collect temporal co-occurrence signals to reinforce weak dependency hypotheses.",
    EvidenceChannel.SHARED_RESOURCE: "Instrument shared-resource access to support weak-edge confirmation.",
    EvidenceChannel.WORKFLOW_WINDOW: "Capture workflow-window co-scheduling signals for weak-edge support.",
    EvidenceChannel.STATIC_DECLARED: "Ingest or refresh static declared dependency manifests for this entity.",
}


@dataclass(frozen=True, slots=True)
class ProbePlan:
    """Suggested probe to improve coverage for a specific channel gap."""

    entity_id: str
    channels: tuple[EvidenceChannel, ...]
    rationale: str


def _channel_priority(channel: EvidenceChannel) -> tuple[int, int, str]:
    profile = CHANNEL_PROFILES.get(channel)
    if profile is None:
        return (9, 9, channel.value)
    class_rank = {
        ChannelClass.DIRECT: 0,
        ChannelClass.DECLARED: 1,
        ChannelClass.WEAK: 2,
    }.get(profile.channel_class, 8)
    normative_rank = 0 if profile.normative else 1
    return (class_rank, normative_rank, channel.value)


def plan_probes(
    entity_id: str,
    missing_channels: list[EvidenceChannel],
    policy: PolicyConfig | None = None,
) -> list[ProbePlan]:
    """
    Plan evidence probes for missing/suppressed channels when enabled.

    Prefer normative DIRECT channels. Returns one plan per channel.
    Returns empty list when probe_planning_enabled is False or no channels given.
    """
    cfg = policy or PolicyConfig()
    if not cfg.probe_planning_enabled:
        return []
    if not missing_channels:
        return []

    ordered = sorted(dict.fromkeys(missing_channels), key=_channel_priority)
    return [
        ProbePlan(
            entity_id=entity_id,
            channels=(channel,),
            rationale=_CHANNEL_RATIONALE.get(
                channel,
                f"Increase observability on the {channel.value} channel for this entity.",
            ),
        )
        for channel in ordered
    ]
