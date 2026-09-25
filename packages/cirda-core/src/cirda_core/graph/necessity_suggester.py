"""Suggest-only necessity heuristics (never mutates the graph)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from cirda_core.domain.enums import Criticality, Necessity
from cirda_core.graph.reachability import (
    LOAD_BEARING_NECESSITIES,
    _criticality_at_or_above,
    _edge_necessity,
    critical_descendants,
)


@dataclass(frozen=True, slots=True)
class NecessityHint:
    """Operator-facing suggestion for an unknown edge's necessity."""

    edge_id: str
    source_id: str
    target_id: str
    current_necessity: str
    suggested_necessity: str
    confidence: float
    rationale: str
    signals: dict[str, Any] = field(default_factory=dict)


def _edge_id(graph: nx.DiGraph, u: str, v: str) -> str:
    data = graph.edges[u, v]
    edge = data.get("edge")
    if edge is not None and getattr(edge, "edge_id", None):
        return str(edge.edge_id)
    relation = data.get("relation", "unknown")
    return f"{u}->{v}:{relation}"


def _edge_confidence(graph: nx.DiGraph, u: str, v: str) -> float:
    data = graph.edges[u, v]
    return float(data.get("confidence", 0.0))


def _unknown_edges_from(graph: nx.DiGraph, root: str) -> list[tuple[str, str]]:
    """Unknown-necessity edges whose source is root or a descendant of root."""
    if root not in graph:
        return []
    nodes = {root} | set(nx.descendants(graph, root))
    edges: list[tuple[str, str]] = []
    for u, v in graph.edges():
        if u not in nodes:
            continue
        if _edge_necessity(graph, u, v) != Necessity.UNKNOWN.value:
            continue
        edges.append((u, v))
    return edges


def _without_edge(graph: nx.DiGraph, u: str, v: str) -> nx.DiGraph:
    copy = graph.copy()
    if copy.has_edge(u, v):
        copy.remove_edge(u, v)
    return copy


def _on_path_to_critical(
    graph: nx.DiGraph,
    root: str,
    u: str,
    v: str,
    criticals: frozenset[str],
) -> bool:
    """True if some root→critical simple path uses edge u→v."""
    if not graph.has_edge(u, v) or root not in graph:
        return False
    for crit in criticals:
        if crit not in graph:
            continue
        if not nx.has_path(graph, root, crit):
            continue
        try:
            for path in nx.all_simple_paths(graph, root, crit, cutoff=12):
                for i in range(len(path) - 1):
                    if path[i] == u and path[i + 1] == v:
                        return True
        except nx.NetworkXError:
            continue
    return False


def suggest_necessity(
    graph: nx.DiGraph,
    source_id: str,
    *,
    criticality_threshold: Criticality = Criticality.HIGH,
) -> list[NecessityHint]:
    """
    Suggest necessity labels for UNKNOWN edges under source_id.

    Heuristics (suggest-only; does not mutate graph or call update APIs):
    - required: removing the edge drops ≥1 critical descendant (load-bearing cut)
    - redundant: edge lies on a path to a critical node but is not a cut (alternate path exists)
    - optional: edge is not on any path from source to a critical descendant
    """
    if source_id not in graph:
        return []

    critical_levels = _criticality_at_or_above(criticality_threshold)
    baseline = critical_descendants(
        graph,
        source_id,
        criticality_threshold=criticality_threshold,
        load_bearing_only=True,
    )
    baseline_crit = baseline.reachable
    hints: list[NecessityHint] = []

    for u, v in _unknown_edges_from(graph, source_id):
        # Only consider load-bearing-classified unknowns (always true for UNKNOWN).
        if _edge_necessity(graph, u, v) not in LOAD_BEARING_NECESSITIES:
            continue

        g2 = _without_edge(graph, u, v)
        after = critical_descendants(
            g2,
            source_id,
            criticality_threshold=criticality_threshold,
            load_bearing_only=True,
        )
        lost = frozenset(baseline_crit - after.reachable)
        conf = _edge_confidence(graph, u, v)
        target_crit = graph.nodes.get(v, {}).get("criticality") in critical_levels
        eid = _edge_id(graph, u, v)

        if lost:
            hints.append(
                NecessityHint(
                    edge_id=eid,
                    source_id=u,
                    target_id=v,
                    current_necessity=Necessity.UNKNOWN.value,
                    suggested_necessity=Necessity.REQUIRED.value,
                    confidence=0.92,
                    rationale=(
                        "Edge is a load-bearing cut: removing it loses critical reachability "
                        f"to {sorted(lost)}."
                    ),
                    signals={
                        "is_critical_bridge": True,
                        "lost_critical": sorted(lost),
                        "target_criticality": graph.nodes.get(v, {}).get("criticality"),
                        "edge_confidence": conf,
                    },
                )
            )
            continue

        on_critical_path = _on_path_to_critical(graph, source_id, u, v, baseline_crit)
        # Alternate route still reaches the same critical set without this edge.
        alt_preserves_criticals = after.reachable == baseline_crit and bool(baseline_crit)

        if on_critical_path and alt_preserves_criticals:
            hints.append(
                NecessityHint(
                    edge_id=eid,
                    source_id=u,
                    target_id=v,
                    current_necessity=Necessity.UNKNOWN.value,
                    suggested_necessity=Necessity.REDUNDANT.value,
                    confidence=0.78,
                    rationale=(
                        "Edge lies on a path toward critical dependents, but an alternate "
                        "load-bearing route remains after removal."
                    ),
                    signals={
                        "is_critical_bridge": False,
                        "alternate_preserves_criticals": True,
                        "target_criticality": graph.nodes.get(v, {}).get("criticality"),
                        "edge_confidence": conf,
                    },
                )
            )
            continue

        if not on_critical_path and not target_crit:
            hints.append(
                NecessityHint(
                    edge_id=eid,
                    source_id=u,
                    target_id=v,
                    current_necessity=Necessity.UNKNOWN.value,
                    suggested_necessity=Necessity.OPTIONAL.value,
                    confidence=0.7,
                    rationale=(
                        "Edge does not lie on a load-bearing path from the source to any "
                        "critical descendant; safe candidate for optional."
                    ),
                    signals={
                        "is_critical_bridge": False,
                        "on_critical_path": False,
                        "target_criticality": graph.nodes.get(v, {}).get("criticality"),
                        "edge_confidence": conf,
                    },
                )
            )

    # Prefer higher-confidence / required first
    hints.sort(key=lambda h: (-h.confidence, h.edge_id))
    return hints
