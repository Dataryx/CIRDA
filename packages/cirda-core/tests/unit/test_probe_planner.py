"""Unit tests for probe planning."""

from __future__ import annotations

import pytest

from cirda_core.config.policy import PolicyConfig
from cirda_core.coverage.inputs import CoverageInputs
from cirda_core.decision.probe_planner import estimate_probe_delta_c, plan_probes
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
    assert all(p.expected_delta_c == 0.0 for p in plans)


def test_estimate_probe_delta_c_restoring_suppressed_channel() -> None:
    entities = frozenset({f"e{i}" for i in range(10)})
    observed = frozenset({f"e{i}" for i in range(8)})
    inputs = CoverageInputs(
        observed_entity_ids=observed,
        total_entity_ids=entities,
        suppressed_channels=frozenset(
            {EvidenceChannel.DATABASE, EvidenceChannel.MESSAGING}
        ),
    )
    delta = estimate_probe_delta_c(inputs, frozenset({EvidenceChannel.DATABASE}))
    assert delta > 0.0


def test_estimate_probe_delta_c_non_suppressed_is_zero() -> None:
    inputs = CoverageInputs(
        observed_entity_ids=frozenset({"a", "b"}),
        total_entity_ids=frozenset({"a", "b", "c"}),
        suppressed_channels=frozenset({EvidenceChannel.DATABASE}),
    )
    delta = estimate_probe_delta_c(inputs, frozenset({EvidenceChannel.TRACE}))
    assert delta == pytest.approx(0.0)


def test_plan_probes_includes_positive_delta_c() -> None:
    entities = frozenset({f"e{i}" for i in range(10)})
    observed = frozenset({f"e{i}" for i in range(9)})
    inputs = CoverageInputs(
        observed_entity_ids=observed,
        total_entity_ids=entities,
        suppressed_channels=frozenset(
            {EvidenceChannel.DATABASE, EvidenceChannel.MESSAGING}
        ),
    )
    plans = plan_probes(
        "vendor-risk-agent",
        [EvidenceChannel.DATABASE, EvidenceChannel.MESSAGING],
        PolicyConfig(probe_planning_enabled=True),
        coverage_inputs=inputs,
    )
    assert len(plans) == 2
    assert all(p.expected_delta_c > 0.0 for p in plans)
