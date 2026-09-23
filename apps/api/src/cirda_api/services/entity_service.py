"""Entity CRUD service."""

from __future__ import annotations

from typing import Any

from cirda_api.db.repositories.entity import EntityRepository


class EntityService:
    def __init__(self, repo: EntityRepository) -> None:
        self.repo = repo

    async def list_entities(
        self,
        *,
        entity_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        return await self.repo.list_entities(entity_type=entity_type, offset=offset, limit=limit)

    async def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        return await self.repo.get_entity(entity_id)

    async def upsert_entity(
        self,
        *,
        entity_id: str,
        entity_type: str,
        name: str,
        criticality: str = "unknown",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await self.repo.upsert_entity(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            criticality=criticality,
            metadata=metadata,
        )
