"""Incremental evidence updates."""

from __future__ import annotations

from dataclasses import dataclass

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.event import EvidenceEvent
from cirda_core.graph.temporal_graph import TemporalGraph
from cirda_core.inference.candidate_generator import generate_candidate_edge, group_events
from cirda_core.ports.clock import Clock
from cirda_core.config.policy import PolicyConfig


@dataclass
class IncrementalUpdateResult:
    """Result of incremental graph update."""

    added_edges: list[DependencyEdge]
    updated_edges: list[DependencyEdge]
    events_processed: int


def apply_events_incrementally(
    graph: TemporalGraph,
    events: list[EvidenceEvent],
    clock: Clock,
    policy: PolicyConfig | None = None,
) -> IncrementalUpdateResult:
    """Apply new evidence events incrementally to temporal graph."""
    groups = group_events(events)
    added: list[DependencyEdge] = []
    updated: list[DependencyEdge] = []

    for pair in groups.values():
        edge = generate_candidate_edge(pair, clock, policy)
        if edge is None:
            continue
        key = edge.edge_id or f"{edge.source_id}->{edge.target_id}:{edge.relation.value}"
        existing = graph.confirmed_edges.get(key) or graph.possible_edges.get(key)
        graph.add_edge(edge)
        if existing is None:
            added.append(edge)
        else:
            updated.append(edge)

    return IncrementalUpdateResult(
        added_edges=added,
        updated_edges=updated,
        events_processed=len(events),
    )
