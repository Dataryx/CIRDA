"""INV-001: blast radius uses possible layer only."""

from __future__ import annotations

import networkx as nx

from cirda_core.analysis.blast_radius import compute_blast_radius
from cirda_core.domain.enums import Criticality, GraphLayer
from cirda_core.graph.kernel import build_digraph
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import Relation


def test_INV_001_blast_radius_uses_possible_layer() -> None:
    confirmed_only = DependencyEdge(
        source_id="A",
        target_id="B",
        relation=Relation.CALLS,
        layer=GraphLayer.CONFIRMED,
        confidence=0.95,
    )
    possible_only = DependencyEdge(
        source_id="A",
        target_id="C",
        relation=Relation.CALLS,
        layer=GraphLayer.POSSIBLE,
        confidence=0.4,
    )
    g_confirmed = build_digraph([], [confirmed_only])
    g_possible = build_digraph([], [possible_only])
    for g in (g_confirmed, g_possible):
        for node in g.nodes:
            g.nodes[node]["criticality"] = Criticality.CRITICAL.value

    blast_from_confirmed = compute_blast_radius(g_confirmed, "A")
    blast_from_possible = compute_blast_radius(g_possible, "A")

    assert blast_from_possible.layer == GraphLayer.POSSIBLE
    assert "C" in blast_from_possible.critical_reachable
    assert blast_from_confirmed.critical_reachable == frozenset({"B"})
    assert blast_from_possible.critical_reachable == frozenset({"C"})
