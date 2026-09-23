"""Temporal dependency graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import GraphLayer
from cirda_core.graph.kernel import build_digraph
from cirda_core.graph.snapshot import GraphSnapshot
from cirda_core.version import ENGINE_VERSION


@dataclass
class TemporalGraph:
    """In-memory temporal graph with confirmed and possible layers."""

    entities: dict[str, Entity] = field(default_factory=dict)
    confirmed_edges: dict[str, DependencyEdge] = field(default_factory=dict)
    possible_edges: dict[str, DependencyEdge] = field(default_factory=dict)

    def add_entity(self, entity: Entity) -> None:
        self.entities[entity.entity_id] = entity

    def add_edge(self, edge: DependencyEdge) -> None:
        key = edge.edge_id or f"{edge.source_id}->{edge.target_id}:{edge.relation.value}"
        if edge.layer == GraphLayer.CONFIRMED:
            self.confirmed_edges[key] = edge
            self.possible_edges.pop(key, None)
        else:
            if key not in self.confirmed_edges:
                self.possible_edges[key] = edge

    def get_edges(self, layer: GraphLayer | None = None) -> list[DependencyEdge]:
        if layer == GraphLayer.CONFIRMED:
            return list(self.confirmed_edges.values())
        if layer == GraphLayer.POSSIBLE:
            return list(self.possible_edges.values()) + list(self.confirmed_edges.values())
        return list(self.confirmed_edges.values()) + list(self.possible_edges.values())

    def snapshot(self, layer: GraphLayer, captured_at: datetime) -> GraphSnapshot:
        edges = self.get_edges(layer)
        layer_edges = [e for e in edges if e.layer == layer or layer == GraphLayer.POSSIBLE]
        if layer == GraphLayer.POSSIBLE:
            layer_edges = self.get_edges(GraphLayer.POSSIBLE)
        else:
            layer_edges = list(self.confirmed_edges.values())
        return GraphSnapshot(
            entities=tuple(self.entities.values()),
            edges=tuple(layer_edges),
            layer=layer,
            captured_at=captured_at,
            version=ENGINE_VERSION,
        )

    def to_digraph(self, layer: GraphLayer) -> "networkx.DiGraph":
        import networkx as nx

        entities = list(self.entities.values())
        if layer == GraphLayer.CONFIRMED:
            edges = list(self.confirmed_edges.values())
        else:
            edges = self.get_edges(GraphLayer.POSSIBLE)
        return build_digraph(entities, edges, layer=None)
