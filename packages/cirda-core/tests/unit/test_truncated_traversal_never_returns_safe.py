"""Truncated traversal never returns SAFE."""

from __future__ import annotations

import networkx as nx

from cirda_core.config.constants import C_MIN
from cirda_core.decision.gate import evaluate_gate
from cirda_core.domain.enums import Criticality, Verdict


def _deep_chain(depth: int) -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    for i in range(depth):
        g.add_node(f"n{i}", criticality=Criticality.LOW.value)
        if i > 0:
            g.add_edge(f"n{i-1}", f"n{i}", confidence=0.9)
    return g


def test_truncated_traversal_never_returns_safe() -> None:
    g = _deep_chain(50)
    decision = evaluate_gate(
        possible_graph=g,
        source_entity_id="n0",
        coverage=C_MIN,
        max_depth=2,
    )
    assert decision.truncated
    assert decision.verdict != Verdict.SAFE
    assert decision.verdict == Verdict.INDETERMINATE
