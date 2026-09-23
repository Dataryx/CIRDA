"""Mediated dependency chain: A writes D, C reads D -> A->D->C."""

from __future__ import annotations

import networkx as nx

from cirda_core.domain.enums import GraphLayer, Relation
from cirda_core.graph.kernel import build_digraph
from cirda_core.inference.direction import translate_to_dependency_edge


def test_mediated_dependency_chain() -> None:
    write_edge = translate_to_dependency_edge(
        actor_id="A",
        counterpart_id="D",
        relation=Relation.WRITES,
        layer=GraphLayer.CONFIRMED,
        confidence=0.9,
    )
    read_edge = translate_to_dependency_edge(
        actor_id="C",
        counterpart_id="D",
        relation=Relation.READS,
        layer=GraphLayer.CONFIRMED,
        confidence=0.9,
    )
    assert write_edge.source_id == "A"
    assert write_edge.target_id == "D"
    assert read_edge.source_id == "D"
    assert read_edge.target_id == "C"

    graph = build_digraph([], [write_edge, read_edge])
    assert nx.has_path(graph, "A", "C")
    path = nx.shortest_path(graph, "A", "C")
    assert path == ["A", "D", "C"]
