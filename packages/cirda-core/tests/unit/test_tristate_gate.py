"""Tri-state gate tests."""

from __future__ import annotations

import networkx as nx
import pytest

from cirda_core.config.constants import C_MIN
from cirda_core.config.policy import PolicyConfig
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.enums import Criticality, Verdict


def _graph_with_critical_child() -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    g.add_node("critical", criticality=Criticality.CRITICAL.value)
    g.add_edge("source", "critical", confidence=0.9)
    return g


def _empty_graph() -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    g.add_node("source", criticality=Criticality.LOW.value)
    return g


def test_unsafe_when_critical_reachable() -> None:
    decision = evaluate_gate(
        possible_graph=_graph_with_critical_child(),
        source_entity_id="source",
        coverage=1.0,
    )
    assert decision.verdict == Verdict.UNSAFE


def test_safe_when_all_clear() -> None:
    decision = evaluate_gate(
        possible_graph=_empty_graph(),
        source_entity_id="source",
        coverage=C_MIN,
    )
    assert decision.verdict == Verdict.SAFE


def test_indeterminate_low_coverage() -> None:
    decision = evaluate_gate(
        possible_graph=_empty_graph(),
        source_entity_id="source",
        coverage=C_MIN - 0.01,
    )
    assert decision.verdict == Verdict.INDETERMINATE


def test_indeterminate_hard_blocks() -> None:
    policy = PolicyConfig(hard_blocks=frozenset({"block-1"}))
    decision = evaluate_gate(
        possible_graph=_empty_graph(),
        source_entity_id="source",
        coverage=1.0,
        policy=policy,
    )
    assert decision.verdict == Verdict.INDETERMINATE


def test_never_boolean_verdict() -> None:
    decision = evaluate_gate(
        possible_graph=_empty_graph(),
        source_entity_id="source",
        coverage=1.0,
    )
    assert isinstance(decision.verdict, Verdict)
    assert decision.verdict in {Verdict.SAFE, Verdict.UNSAFE, Verdict.INDETERMINATE}
