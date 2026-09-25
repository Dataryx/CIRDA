"""Enumerate load-bearing critical dependency paths."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from cirda_core.analysis.path_confidence import path_confidence
from cirda_core.domain.enums import Criticality
from cirda_core.graph.reachability import (
    LOAD_BEARING_NECESSITIES,
    _criticality_at_or_above,
    _edge_necessity,
    critical_descendants,
)


@dataclass(frozen=True, slots=True)
class CriticalPath:
    """A directed path from source to a critical descendant."""

    path_nodes: tuple[str, ...]
    path_confidence: float
    is_critical_path: bool = True


def _load_bearing_subgraph(graph: nx.DiGraph) -> nx.DiGraph:
    """View containing only load-bearing edges (optional/redundant removed)."""
    sub = nx.DiGraph()
    sub.add_nodes_from(graph.nodes(data=True))
    for u, v, data in graph.edges(data=True):
        necessity = data.get("necessity")
        if necessity is None:
            necessity = _edge_necessity(graph, u, v)
        if str(necessity) in LOAD_BEARING_NECESSITIES:
            sub.add_edge(u, v, **data)
    return sub


def enumerate_critical_paths(
    graph: nx.DiGraph,
    source_id: str,
    *,
    criticality_threshold: Criticality = Criticality.HIGH,
    target_id: str | None = None,
    max_depth: int = 8,
    max_paths: int = 32,
) -> list[CriticalPath]:
    """
    Enumerate simple load-bearing paths from source to critical dependents.

    Optional/redundant edges are excluded. Results are sorted by descending
    path confidence. Bounded by max_depth and max_paths.
    """
    if source_id not in graph:
        return []

    lb = _load_bearing_subgraph(graph)
    if source_id not in lb:
        return []

    if target_id is not None:
        targets = frozenset({target_id}) if target_id in lb else frozenset()
    else:
        targets = critical_descendants(
            lb,
            source_id,
            criticality_threshold=criticality_threshold,
            max_depth=max_depth,
            load_bearing_only=True,
        ).reachable

    if not targets:
        return []

    critical_levels = _criticality_at_or_above(criticality_threshold)
    paths: list[CriticalPath] = []
    for target in sorted(targets):
        if target == source_id:
            continue
        if target_id is None and lb.nodes.get(target, {}).get("criticality") not in critical_levels:
            continue
        if not nx.has_path(lb, source_id, target):
            continue
        try:
            for node_path in nx.all_simple_paths(lb, source_id, target, cutoff=max_depth):
                conf = path_confidence(lb, list(node_path))
                paths.append(
                    CriticalPath(
                        path_nodes=tuple(node_path),
                        path_confidence=round(conf, 6),
                        is_critical_path=True,
                    )
                )
                if len(paths) >= max_paths:
                    paths.sort(key=lambda p: (-p.path_confidence, p.path_nodes))
                    return paths[:max_paths]
        except nx.NetworkXError:
            continue

    paths.sort(key=lambda p: (-p.path_confidence, p.path_nodes))
    return paths[:max_paths]
