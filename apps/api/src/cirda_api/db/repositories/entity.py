"""Entity repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.entity import Entity as EntityModel
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Criticality, EntityType


class EntityRepository(RepositoryBase):
    async def list_entities(
        self,
        *,
        entity_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = [
                {
                    "entity_id": e.entity_id,
                    "entity_type": e.entity_type.value,
                    "name": e.name,
                    "criticality": e.criticality.value,
                    "metadata": {},
                }
                for e in self.memory.entities.values()
            ]
            if entity_type:
                rows = [r for r in rows if r["entity_type"] == entity_type]
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = select(EntityModel)
        if entity_type:
            q = q.where(EntityModel.entity_type == entity_type)
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = result.scalars().all()
        count_result = await self.session.execute(select(EntityModel))
        total = len(count_result.scalars().all())
        return [
            {
                "entity_id": e.entity_id,
                "entity_type": e.entity_type,
                "name": e.name,
                "criticality": e.criticality,
                "metadata": e.metadata_json,
                "created_at": e.created_at,
                "updated_at": e.updated_at,
            }
            for e in items
        ], total

    async def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        if self.memory:
            e = self.memory.entities.get(entity_id)
            if not e:
                return None
            return {
                "entity_id": e.entity_id,
                "entity_type": e.entity_type.value,
                "name": e.name,
                "criticality": e.criticality.value,
                "metadata": {},
                "aliases": [a[0] for a in self.memory.aliases.get(entity_id, [])],
            }

        assert self.session is not None
        result = await self.session.execute(select(EntityModel).where(EntityModel.entity_id == entity_id))
        row = result.scalar_one_or_none()
        if not row:
            return None
        return {
            "entity_id": row.entity_id,
            "entity_type": row.entity_type,
            "name": row.name,
            "criticality": row.criticality,
            "metadata": row.metadata_json,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    async def upsert_entity(
        self,
        *,
        entity_id: str,
        entity_type: str,
        name: str,
        criticality: str = "unknown",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = utcnow()
        if self.memory:
            return self.memory.upsert_entity_record(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                criticality=criticality,
                metadata=metadata,
                now=now,
            )

        assert self.session is not None
        result = await self.session.get(EntityModel, entity_id)
        if result:
            result.name = name
            result.entity_type = entity_type
            result.criticality = criticality
            result.metadata_json = metadata or {}
            result.updated_at = now
            row = result
        else:
            row = EntityModel(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                criticality=criticality,
                metadata_json=metadata or {},
                created_at=now,
                updated_at=now,
            )
            self.session.add(row)
        await self.session.commit()
        return {
            "entity_id": row.entity_id,
            "entity_type": row.entity_type,
            "name": row.name,
            "criticality": row.criticality,
            "metadata": row.metadata_json,
        }

    def to_domain(self, record: dict[str, Any]) -> Entity:
        return Entity(
            entity_id=record["entity_id"],
            entity_type=EntityType(record["entity_type"]),
            name=record["name"],
            criticality=Criticality(record.get("criticality", "unknown")),
        )
