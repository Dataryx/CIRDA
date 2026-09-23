"""Path confidence computation."""

from __future__ import annotations

import networkx as nx


def path_confidence(graph: nx.DiGraph, path: list[str]) -> float:
    """
    Compute path confidence as product of edge confidences.

    Returns 0.0 for invalid paths.
    """
    if len(path) < 2:
        return 1.0
    confidence = 1.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if not graph.has_edge(u, v):
            return 0.0
        edge_conf = graph.edges[u, v].get("confidence", 0.0)
        confidence *= float(edge_conf)
    return confidence


def weakest_link_confidence(graph: nx.DiGraph, path: list[str]) -> float:
    """Return minimum edge confidence along a path."""
    if len(path) < 2:
        return 1.0
    min_conf = 1.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if not graph.has_edge(u, v):
            return 0.0
        edge_conf = float(graph.edges[u, v].get("confidence", 0.0))
        min_conf = min(min_conf, edge_conf)
    return min_conf
