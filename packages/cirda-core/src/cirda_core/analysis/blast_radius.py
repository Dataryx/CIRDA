"""Blast radius analysis using G_p (INV-001)."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from cirda_core.domain.enums import Criticality, GraphLayer
from cirda_core.graph.reachability import ReachabilityResult, critical_descendants, descendants_within_depth


@dataclass(frozen=True, slots=True)
class BlastRadius:
    """Blast radius computed exclusively from possible layer."""

    source_id: str
    layer: GraphLayer
    all_reachable: frozenset[str]
    critical_reachable: frozenset[str]
    truncated: bool


def compute_blast_radius(
    possible_graph: nx.DiGraph,
    source_id: str,
    criticality_threshold: Criticality = Criticality.HIGH,
    max_depth: int | None = None,
    max_nodes: int | None = None,
) -> BlastRadius:
    """
    Compute blast radius from G_p only (INV-001).

    Never uses confirmed layer graph for reachability.
    """
    all_result: ReachabilityResult = descendants_within_depth(
        possible_graph, source_id, max_depth, max_nodes
    )
    crit_result = critical_descendants(
        possible_graph,
        source_id,
        criticality_threshold,
        max_depth,
        max_nodes,
    )
    return BlastRadius(
        source_id=source_id,
        layer=GraphLayer.POSSIBLE,
        all_reachable=all_result.reachable,
        critical_reachable=crit_result.reachable,
        truncated=all_result.truncated or crit_result.truncated,
    )
