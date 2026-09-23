"""Probe planning (feature-flagged off by default)."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.enums import EvidenceChannel


@dataclass(frozen=True, slots=True)
class ProbePlan:
    """Suggested probes to improve coverage."""

    entity_id: str
    channels: tuple[EvidenceChannel, ...]
    rationale: str


def plan_probes(
    entity_id: str,
    missing_channels: list[EvidenceChannel],
    policy: PolicyConfig | None = None,
) -> list[ProbePlan]:
    """
    Plan evidence probes when enabled.

    Returns empty list when probe_planning_enabled is False.
    """
    cfg = policy or PolicyConfig()
    if not cfg.probe_planning_enabled:
        return []
    if not missing_channels:
        return []
    return [
        ProbePlan(
            entity_id=entity_id,
            channels=tuple(missing_channels),
            rationale="Increase observability for under-covered channels",
        )
    ]
