"""Entity repository."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from cirda_api.db.models.alias import Alias as AliasModel
from cirda_api.db.models.entity import Entity as EntityModel
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import Criticality, EntityType
from cirda_core.resolution.similarity import normalized_key


class EntityRepository(RepositoryBase):
    async def list_entities(
        self,
        *,
        entity_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            from cirda_api.security.tenant import get_current_tenant_id

            tenant = get_current_tenant_id()
            prefix = f"{tenant}::"
            rows = []
            for key, e in self.memory.entities.items():
                if not key.startswith(prefix):
                    continue
                rows.append(
                    {
                        "entity_id": e.entity_id,
                        "entity_type": e.entity_type.value,
                        "name": e.name,
                        "criticality": e.criticality.value,
                        "metadata": dict(self.memory.entity_metadata.get(key, {})),
                        "aliases": sorted(e.aliases),
                        "tenant_id": tenant,
                    }
                )
            if entity_type:
                rows = [r for r in rows if r["entity_type"] == entity_type]
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        from cirda_api.security.tenant import get_current_tenant_id

        tenant = get_current_tenant_id()
        q = select(EntityModel).options(selectinload(EntityModel.aliases)).where(
            EntityModel.tenant_id == tenant
        )
        if entity_type:
            q = q.where(EntityModel.entity_type == entity_type)
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = result.scalars().unique().all()
        count_result = await self.session.execute(
            select(EntityModel).where(EntityModel.tenant_id == tenant)
        )
        total = len(count_result.scalars().all())
        return [self._row_to_dict(e) for e in items], total

    async def get_entity(self, entity_id: str) -> dict[str, Any] | None:
        if self.memory:
            from cirda_api.security.tenant import get_current_tenant_id

            key = f"{get_current_tenant_id()}::{entity_id}"
            e = self.memory.entities.get(key)
            if not e:
                return None
            return {
                "entity_id": e.entity_id,
                "entity_type": e.entity_type.value,
                "name": e.name,
                "criticality": e.criticality.value,
                "metadata": dict(self.memory.entity_metadata.get(key, {})),
                "aliases": [a[0] for a in self.memory.aliases.get(key, [])] or sorted(e.aliases),
                "tenant_id": get_current_tenant_id(),
            }

        assert self.session is not None
        from cirda_api.security.tenant import get_current_tenant_id

        result = await self.session.execute(
            select(EntityModel)
            .options(selectinload(EntityModel.aliases))
            .where(
                EntityModel.entity_id == entity_id,
                EntityModel.tenant_id == get_current_tenant_id(),
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        return self._row_to_dict(row)

    async def upsert_entity(
        self,
        *,
        entity_id: str,
        entity_type: str,
        name: str,
        criticality: str = "unknown",
        metadata: dict[str, Any] | None = None,
        aliases: list[str] | None = None,
    ) -> dict[str, Any]:
        now = utcnow()
        if self.memory:
            return self.memory.upsert_entity_record(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                criticality=criticality,
                metadata=metadata,
                aliases=aliases,
                now=now,
            )

        assert self.session is not None
        result = await self.session.get(
            EntityModel, entity_id, options=[selectinload(EntityModel.aliases)]
        )
        if result:
            result.name = name
            result.entity_type = entity_type
            result.criticality = criticality
            result.metadata_json = metadata or {}
            result.updated_at = now
            row = result
        else:
            from cirda_api.security.tenant import get_current_tenant_id

            row = EntityModel(
                entity_id=entity_id,
                entity_type=entity_type,
                name=name,
                criticality=criticality,
                tenant_id=get_current_tenant_id(),
                metadata_json=metadata or {},
                created_at=now,
                updated_at=now,
            )
            self.session.add(row)
            await self.session.flush()

        if aliases is not None:
            desired = {a.strip() for a in aliases if a and a.strip()}
            existing_by_alias = {a.alias: a for a in list(row.aliases or [])}
            for alias, model in existing_by_alias.items():
                if alias not in desired:
                    await self.session.delete(model)
            for alias in desired:
                if alias not in existing_by_alias:
                    self.session.add(
                        AliasModel(
                            alias_id=str(uuid.uuid4()),
                            entity_id=entity_id,
                            alias=alias,
                            source="api",
                            created_at=now,
                        )
                    )

        await self.session.commit()
        refreshed = await self.get_entity(entity_id)
        assert refreshed is not None
        return refreshed

    def to_domain(self, record: dict[str, Any]) -> Entity:
        return Entity(
            entity_id=record["entity_id"],
            entity_type=EntityType(record["entity_type"]),
            name=record["name"],
            criticality=Criticality(record.get("criticality", "unknown")),
            aliases=frozenset(record.get("aliases") or []),
        )

    async def resolve_entity_id(self, raw_id: str) -> str:
        """
        Map an external id to a canonical entity id when uniquely aliased.

        - If ``raw_id`` is already a registered entity id, return it.
        - If exactly one entity claims ``raw_id`` as an alias, return that entity.
        - Otherwise passthrough (unknown or ambiguous alias collision).
        """
        if not raw_id:
            return raw_id
        existing = await self.get_entity(raw_id)
        if existing:
            return raw_id
        owners = await self.find_entity_ids_by_alias(raw_id)
        if len(owners) == 1:
            return next(iter(owners))
        return raw_id

    async def find_entity_ids_by_alias(self, alias: str) -> set[str]:
        key = normalized_key(alias)
        if not key:
            return set()

        if self.memory:
            owners: set[str] = set()
            for entity in self.memory.entities.values():
                for candidate in entity.aliases:
                    if normalized_key(candidate) == key:
                        owners.add(entity.entity_id)
            for entity_id, alias_rows in self.memory.aliases.items():
                for candidate, _src in alias_rows:
                    if normalized_key(candidate) == key:
                        owners.add(entity_id)
            return owners

        assert self.session is not None
        result = await self.session.execute(select(AliasModel))
        return {
            row.entity_id
            for row in result.scalars().all()
            if normalized_key(row.alias) == key
        }

    @staticmethod
    def _row_to_dict(row: EntityModel) -> dict[str, Any]:
        return {
            "entity_id": row.entity_id,
            "entity_type": row.entity_type,
            "name": row.name,
            "criticality": row.criticality,
            "metadata": row.metadata_json,
            "aliases": [a.alias for a in (row.aliases or [])],
            "tenant_id": getattr(row, "tenant_id", "default"),
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
