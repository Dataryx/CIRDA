"""Reachability bounds tests."""

from __future__ import annotations

import networkx as nx

from cirda_core.domain.enums import Criticality
from cirda_core.graph.reachability import critical_descendants, descendants_within_depth


def _chain_graph(n: int) -> nx.DiGraph:
    g: nx.DiGraph = nx.DiGraph()
    for i in range(n):
        g.add_node(f"n{i}", criticality=Criticality.HIGH.value if i == n - 1 else Criticality.LOW.value)
        if i > 0:
            g.add_edge(f"n{i-1}", f"n{i}", confidence=0.9)
    return g


def test_depth_bound_truncates() -> None:
    g = _chain_graph(10)
    result = descendants_within_depth(g, "n0", max_depth=3)
    assert len(result.reachable) == 3
    assert result.truncated


def test_node_bound_truncates() -> None:
    g = _chain_graph(20)
    result = descendants_within_depth(g, "n0", max_nodes=5)
    assert result.truncated
    assert result.visited_count <= 5


def test_critical_descendants() -> None:
    g = _chain_graph(5)
    result = critical_descendants(g, "n0", Criticality.HIGH)
    assert "n4" in result.reachable
