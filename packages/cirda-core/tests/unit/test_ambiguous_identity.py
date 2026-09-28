"""Identity ambiguity blocks SAFE (no false-SAFE with split identity)."""

from __future__ import annotations

import networkx as nx

from cirda_core.config.policy import PolicyConfig
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Criticality, EntityType, Verdict
from cirda_core.resolution.ambiguity import detect_identity_ambiguity


def test_detect_orphan_alias_node() -> None:
    canonical = Entity(
        entity_id="vendor-risk-agent",
        entity_type=EntityType.AGENT,
        name="Vendor Risk Agent",
        aliases=frozenset({"vendor_risk"}),
    )
    orphan = Entity(
        entity_id="vendor_risk",
        entity_type=EntityType.AGENT,
        name="vendor_risk",
    )
    result = detect_identity_ambiguity(
        entity_id="vendor-risk-agent",
        entities=[canonical, orphan],
    )
    assert result.is_ambiguous
    assert "vendor_risk" in result.conflicting_ids


def test_detect_alias_collision() -> None:
    a = Entity(
        entity_id="agent-a",
        entity_type=EntityType.AGENT,
        name="A",
        aliases=frozenset({"shared"}),
    )
    b = Entity(
        entity_id="agent-b",
        entity_type=EntityType.AGENT,
        name="B",
        aliases=frozenset({"shared"}),
    )
    result = detect_identity_ambiguity(entity_id="agent-a", entities=[a, b])
    assert result.is_ambiguous
    assert "agent-b" in result.conflicting_ids


def test_no_ambiguity_when_aliases_unique() -> None:
    a = Entity(
        entity_id="agent-a",
        entity_type=EntityType.AGENT,
        name="A",
        aliases=frozenset({"only-a"}),
    )
    b = Entity(
        entity_id="agent-b",
        entity_type=EntityType.AGENT,
        name="B",
        aliases=frozenset({"only-b"}),
    )
    result = detect_identity_ambiguity(entity_id="agent-a", entities=[a, b])
    assert not result.is_ambiguous


def test_gate_ambiguous_identity_blocks_safe() -> None:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    decision = evaluate_gate(
        possible_graph=g,
        source_entity_id="source",
        coverage=1.0,
        policy=PolicyConfig(),
        ambiguous_identity=True,
    )
    assert decision.verdict == Verdict.INDETERMINATE
    assert decision.verdict != Verdict.SAFE
    assert "ambiguous_identity" in decision.reason_codes


def test_gate_combines_coverage_and_identity_codes() -> None:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    decision = evaluate_gate(
        possible_graph=g,
        source_entity_id="source",
        coverage=0.5,
        policy=PolicyConfig(c_min=0.85),
        ambiguous_identity=True,
    )
    assert decision.verdict == Verdict.INDETERMINATE
    assert "coverage_below_threshold" in decision.reason_codes
    assert "ambiguous_identity" in decision.reason_codes
