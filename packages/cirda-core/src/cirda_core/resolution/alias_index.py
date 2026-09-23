"""Alias index for entity resolution."""

from __future__ import annotations

from cirda_core.domain.entity import Entity
from cirda_core.resolution.similarity import normalized_key


class AliasIndex:
    """Index entity IDs and aliases for lookup."""

    def __init__(self) -> None:
        self._by_key: dict[str, str] = {}
        self._entities: dict[str, Entity] = {}

    def add(self, entity: Entity) -> None:
        self._entities[entity.entity_id] = entity
        self._by_key[normalized_key(entity.entity_id)] = entity.entity_id
        self._by_key[normalized_key(entity.name)] = entity.entity_id
        for alias in entity.aliases:
            self._by_key[normalized_key(alias)] = entity.entity_id

    def lookup(self, key: str) -> str | None:
        return self._by_key.get(normalized_key(key))

    def get_entity(self, entity_id: str) -> Entity | None:
        return self._entities.get(entity_id)

    def all_entities(self) -> list[Entity]:
        return list(self._entities.values())
