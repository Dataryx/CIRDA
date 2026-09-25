"""Necessity-aware critical reachability and gate behavior."""

from __future__ import annotations

import networkx as nx

from cirda_core.analysis.blast_radius import compute_blast_radius
from cirda_core.config.constants import C_MIN
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import (
    Criticality,
    EntityType,
    GraphLayer,
    Necessity,
    Relation,
    Verdict,
)
from cirda_core.graph.kernel import build_digraph
from cirda_core.graph.reachability import critical_descendants


def _entities() -> list[Entity]:
    return [
        Entity(entity_id="A", entity_type=EntityType.AGENT, name="A", criticality=Criticality.LOW),
        Entity(
            entity_id="B",
            entity_type=EntityType.SERVICE,
            name="B",
            criticality=Criticality.CRITICAL,
        ),
    ]


def _edge(necessity: Necessity) -> DependencyEdge:
    return DependencyEdge(
        source_id="A",
        target_id="B",
        relation=Relation.CALLS,
        layer=GraphLayer.POSSIBLE,
        confidence=0.9,
        necessity=necessity,
    )


def test_unknown_necessity_still_unsafe() -> None:
    g = build_digraph(_entities(), [_edge(Necessity.UNKNOWN)], GraphLayer.POSSIBLE)
    decision = evaluate_gate(possible_graph=g, source_entity_id="A", coverage=1.0)
    assert decision.verdict == Verdict.UNSAFE
    assert "critical_descendant_reachable" in decision.reason_codes


def test_required_and_fallback_remain_load_bearing() -> None:
    for necessity in (Necessity.REQUIRED, Necessity.FALLBACK):
        g = build_digraph(_entities(), [_edge(necessity)], GraphLayer.POSSIBLE)
        decision = evaluate_gate(possible_graph=g, source_entity_id="A", coverage=1.0)
        assert decision.verdict == Verdict.UNSAFE, necessity


def test_optional_path_to_critical_does_not_force_unsafe() -> None:
    g = build_digraph(_entities(), [_edge(Necessity.OPTIONAL)], GraphLayer.POSSIBLE)
    decision = evaluate_gate(possible_graph=g, source_entity_id="A", coverage=C_MIN)
    assert decision.verdict == Verdict.SAFE
    assert "optional_or_redundant_paths_ignored" in decision.reason_codes
    assert "all_checks_passed" in decision.reason_codes
    assert "critical_descendant_reachable" not in decision.reason_codes


def test_redundant_path_to_critical_does_not_force_unsafe() -> None:
    g = build_digraph(_entities(), [_edge(Necessity.REDUNDANT)], GraphLayer.POSSIBLE)
    decision = evaluate_gate(possible_graph=g, source_entity_id="A", coverage=C_MIN)
    assert decision.verdict == Verdict.SAFE
    assert "optional_or_redundant_paths_ignored" in decision.reason_codes


def test_blast_critical_skips_optional_but_all_reachable_includes() -> None:
    g = build_digraph(_entities(), [_edge(Necessity.OPTIONAL)], GraphLayer.POSSIBLE)
    blast = compute_blast_radius(g, "A")
    assert "B" in blast.all_reachable
    assert "B" not in blast.critical_reachable


def test_critical_descendants_default_load_bearing() -> None:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("A", criticality=Criticality.LOW.value)
    g.add_node("B", criticality=Criticality.CRITICAL.value)
    g.add_edge("A", "B", necessity=Necessity.OPTIONAL.value, confidence=0.9)
    assert critical_descendants(g, "A").reachable == frozenset()
    assert critical_descendants(g, "A", load_bearing_only=False).reachable == frozenset({"B"})
