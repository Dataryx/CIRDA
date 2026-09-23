"""Graph reachability with bounds."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from cirda_core.domain.enums import Criticality


@dataclass(frozen=True, slots=True)
class ReachabilityResult:
    """Bounded reachability traversal result."""

    reachable: frozenset[str]
    truncated: bool
    visited_count: int
    max_depth_reached: int


def descendants_within_depth(
    graph: nx.DiGraph,
    source: str,
    max_depth: int | None = None,
    max_nodes: int | None = None,
) -> ReachabilityResult:
    """
    Traverse descendants from source with optional depth and node caps.

    Returns truncated=True if caps were hit before full exploration.
    """
    if source not in graph:
        return ReachabilityResult(
            reachable=frozenset(),
            truncated=False,
            visited_count=0,
            max_depth_reached=0,
        )

    reachable: set[str] = set()
    truncated = False
    max_depth_reached = 0
    queue: list[tuple[str, int]] = [(source, 0)]
    visited: set[str] = {source}

    while queue:
        node, depth = queue.pop(0)
        if depth > 0:
            reachable.add(node)
        max_depth_reached = max(max_depth_reached, depth)

        if max_depth is not None and depth >= max_depth:
            if any(graph.successors(node)):
                truncated = True
            continue

        for successor in graph.successors(node):
            if successor in visited:
                continue
            if max_nodes is not None and len(visited) >= max_nodes:
                truncated = True
                return ReachabilityResult(
                    reachable=frozenset(reachable),
                    truncated=truncated,
                    visited_count=len(visited),
                    max_depth_reached=max_depth_reached,
                )
            visited.add(successor)
            queue.append((successor, depth + 1))

    return ReachabilityResult(
        reachable=frozenset(reachable),
        truncated=truncated,
        visited_count=len(visited),
        max_depth_reached=max_depth_reached,
    )


def critical_descendants(
    graph: nx.DiGraph,
    source: str,
    criticality_threshold: Criticality = Criticality.HIGH,
    max_depth: int | None = None,
    max_nodes: int | None = None,
) -> ReachabilityResult:
    """Find critical descendants reachable from source."""
    result = descendants_within_depth(graph, source, max_depth, max_nodes)
    critical_levels = _criticality_at_or_above(criticality_threshold)
    critical = frozenset(
        node
        for node in result.reachable
        if graph.nodes[node].get("criticality") in critical_levels
    )
    return ReachabilityResult(
        reachable=critical,
        truncated=result.truncated,
        visited_count=result.visited_count,
        max_depth_reached=result.max_depth_reached,
    )


def _criticality_at_or_above(threshold: Criticality) -> frozenset[str]:
    order = [
        Criticality.CRITICAL,
        Criticality.HIGH,
        Criticality.MEDIUM,
        Criticality.LOW,
        Criticality.UNKNOWN,
    ]
    try:
        idx = order.index(threshold)
    except ValueError:
        idx = len(order)
    return frozenset(c.value for c in order[: idx + 1])
