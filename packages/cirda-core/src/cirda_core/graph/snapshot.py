"""Graph snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import networkx as nx

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import GraphLayer


@dataclass(frozen=True, slots=True)
class GraphSnapshot:
    """Immutable point-in-time view of a dependency graph."""

    entities: tuple[Entity, ...]
    edges: tuple[DependencyEdge, ...]
    layer: GraphLayer
    captured_at: datetime
    version: str

    def entity_map(self) -> dict[str, Entity]:
        return {e.entity_id: e for e in self.entities}

    def to_digraph(self) -> nx.DiGraph:
        from cirda_core.graph.kernel import build_digraph

        return build_digraph(list(self.entities), list(self.edges), self.layer)
