"""Entity domain model."""

from __future__ import annotations

from dataclasses import dataclass, field

from cirda_core.domain.enums import Criticality, EntityType


@dataclass(frozen=True, slots=True)
class Entity:
    """A node in the dependency graph."""

    entity_id: str
    entity_type: EntityType
    name: str
    criticality: Criticality = Criticality.UNKNOWN
    aliases: frozenset[str] = field(default_factory=frozenset)
    metadata: frozenset[tuple[str, str]] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id must be non-empty")
        if not self.name:
            raise ValueError("name must be non-empty")
