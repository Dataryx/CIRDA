"""NetworkX graph kernel."""

from __future__ import annotations

from typing import Any

import networkx as nx

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import GraphLayer


def build_digraph(
    entities: list[Entity],
    edges: list[DependencyEdge],
    layer: GraphLayer | None = None,
) -> nx.DiGraph:
    """Build a NetworkX DiGraph from entities and edges."""
    graph: nx.DiGraph = nx.DiGraph()
    for entity in entities:
        graph.add_node(
            entity.entity_id,
            entity=entity,
            criticality=entity.criticality.value,
        )
    for edge in edges:
        if layer is not None and edge.layer != layer:
            continue
        graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge=edge,
            confidence=edge.confidence,
            relation=edge.relation.value,
            layer=edge.layer.value,
        )
    return graph


def merge_graphs(*graphs: nx.DiGraph) -> nx.DiGraph:
    """Merge multiple DiGraphs."""
    merged: nx.DiGraph = nx.DiGraph()
    for graph in graphs:
        merged.update(graph)
    return merged


def edge_data(graph: nx.DiGraph, source: str, target: str) -> dict[str, Any]:
    """Return edge attribute dict or empty dict."""
    if graph.has_edge(source, target):
        return dict(graph.edges[source, target])
    return {}
