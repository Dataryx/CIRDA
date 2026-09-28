"""Alias index for entity resolution."""

from __future__ import annotations

from cirda_core.domain.entity import Entity
from cirda_core.resolution.similarity import normalized_key


class AliasIndex:
    """Index entity IDs and aliases for lookup."""

    def __init__(self) -> None:
        self._by_key: dict[str, set[str]] = {}
        self._entities: dict[str, Entity] = {}

    def add(self, entity: Entity) -> None:
        self._entities[entity.entity_id] = entity
        for raw in (entity.entity_id, entity.name, *entity.aliases):
            key = normalized_key(raw)
            self._by_key.setdefault(key, set()).add(entity.entity_id)

    def lookup(self, key: str) -> str | None:
        """Return canonical id only when the key uniquely maps to one entity."""
        owners = self._by_key.get(normalized_key(key), set())
        if len(owners) == 1:
            return next(iter(owners))
        return None

    def owners(self, key: str) -> frozenset[str]:
        return frozenset(self._by_key.get(normalized_key(key), set()))

    def get_entity(self, entity_id: str) -> Entity | None:
        return self._entities.get(entity_id)

    def all_entities(self) -> list[Entity]:
        return list(self._entities.values())
