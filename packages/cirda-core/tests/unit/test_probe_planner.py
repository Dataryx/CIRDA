"""Unit tests for probe planning."""

from __future__ import annotations

from cirda_core.config.policy import PolicyConfig
from cirda_core.decision.probe_planner import plan_probes
from cirda_core.domain.enums import EvidenceChannel


def test_plan_probes_disabled_returns_empty() -> None:
    plans = plan_probes(
        "vendor-risk-agent",
        [EvidenceChannel.DATABASE, EvidenceChannel.MESSAGING],
        PolicyConfig(probe_planning_enabled=False),
    )
    assert plans == []


def test_plan_probes_empty_channels_returns_empty() -> None:
    plans = plan_probes("agent-a", [], PolicyConfig(probe_planning_enabled=True))
    assert plans == []


def test_plan_probes_one_per_channel_prefers_direct() -> None:
    plans = plan_probes(
        "vendor-risk-agent",
        [
            EvidenceChannel.TEMPORAL_CORRELATION,
            EvidenceChannel.DATABASE,
            EvidenceChannel.MESSAGING,
            EvidenceChannel.DATABASE,  # dedupe
        ],
        PolicyConfig(probe_planning_enabled=True),
    )
    assert len(plans) == 3
    assert plans[0].channels == (EvidenceChannel.DATABASE,)
    assert plans[1].channels == (EvidenceChannel.MESSAGING,)
    assert plans[2].channels == (EvidenceChannel.TEMPORAL_CORRELATION,)
    assert "database" in plans[0].rationale.lower()
    assert all(p.entity_id == "vendor-risk-agent" for p in plans)
