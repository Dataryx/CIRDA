"""Graph store protocol."""

from __future__ import annotations

from typing import Protocol

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import GraphLayer


class GraphStore(Protocol):
    """Persistence port for entities and edges."""

    def get_entity(self, entity_id: str) -> Entity | None:
        ...

    def list_entities(self) -> list[Entity]:
        ...

    def get_edges(
        self,
        layer: GraphLayer | None = None,
        source_id: str | None = None,
        target_id: str | None = None,
    ) -> list[DependencyEdge]:
        ...

    def upsert_entity(self, entity: Entity) -> None:
        ...

    def upsert_edge(self, edge: DependencyEdge) -> None:
        ...
