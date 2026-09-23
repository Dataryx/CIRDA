"""Evidence repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.evidence import EvidenceEvent as EvidenceModel
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore
from cirda_core.domain.enums import EntityType, EvidenceChannel, Relation
from cirda_core.domain.event import EvidenceEvent


class EvidenceRepository(RepositoryBase):
    async def add_event(
        self,
        event: EvidenceEvent,
        *,
        idempotency_key: str | None = None,
    ) -> tuple[EvidenceEvent, bool]:
        if self.memory:
            return self.memory.add_evidence(event, idempotency_key)

        assert self.session is not None
        if idempotency_key:
            existing = await self.session.execute(
                select(EvidenceModel).where(EvidenceModel.idempotency_key == idempotency_key)
            )
            row = existing.scalar_one_or_none()
            if row:
                return self._to_domain(row), False

        now = utcnow()
        model = EvidenceModel(
            event_id=event.event_id,
            idempotency_key=idempotency_key,
            source_id=event.source_id,
            target_id=event.target_id,
            relation=event.relation.value,
            channel=event.channel.value,
            source_type=event.source_type.value if event.source_type else None,
            target_type=event.target_type.value if event.target_type else None,
            payload_hash=event.payload_hash,
            observed_at=event.observed_at,
            ingested_at=now,
        )
        self.session.add(model)
        await self.session.commit()
        return event, True

    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        if self.memory:
            ev = self.memory.evidence_events.get(event_id)
            return self._event_dict(ev) if ev else None

        assert self.session is not None
        row = await self.session.get(EvidenceModel, event_id)
        return self._model_dict(row) if row else None

    async def list_events(
        self,
        *,
        source_id: str | None = None,
        target_id: str | None = None,
        channel: str | None = None,
        as_of: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = [self._event_dict(e) for e in self.memory.evidence_events.values()]
            if source_id:
                rows = [r for r in rows if r["source_id"] == source_id]
            if target_id:
                rows = [r for r in rows if r["target_id"] == target_id]
            if channel:
                rows = [r for r in rows if r["channel"] == channel]
            if as_of:
                rows = [r for r in rows if r["observed_at"] <= as_of]
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = select(EvidenceModel)
        if source_id:
            q = q.where(EvidenceModel.source_id == source_id)
        if target_id:
            q = q.where(EvidenceModel.target_id == target_id)
        if channel:
            q = q.where(EvidenceModel.channel == channel)
        if as_of:
            q = q.where(EvidenceModel.observed_at <= as_of)
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = result.scalars().all()
        all_result = await self.session.execute(q)
        total = len(all_result.scalars().all())
        return [self._model_dict(i) for i in items], total

    async def count_observations(
        self,
        source_id: str,
        target_id: str,
        channel: EvidenceChannel,
        as_of: datetime | None = None,
    ) -> int:
        if self.memory:
            count = 0
            for ev in self.memory.evidence_events.values():
                if ev.source_id == source_id and ev.target_id == target_id and ev.channel == channel:
                    if as_of is None or ev.observed_at <= as_of:
                        count += 1
            return count

        assert self.session is not None
        q = select(EvidenceModel).where(
            EvidenceModel.source_id == source_id,
            EvidenceModel.target_id == target_id,
            EvidenceModel.channel == channel.value,
        )
        if as_of:
            q = q.where(EvidenceModel.observed_at <= as_of)
        result = await self.session.execute(q)
        return len(result.scalars().all())

    @staticmethod
    def _event_dict(ev: EvidenceEvent) -> dict[str, Any]:
        return {
            "event_id": ev.event_id,
            "source_id": ev.source_id,
            "target_id": ev.target_id,
            "relation": ev.relation.value,
            "channel": ev.channel.value,
            "source_type": ev.source_type.value if ev.source_type else None,
            "target_type": ev.target_type.value if ev.target_type else None,
            "payload_hash": ev.payload_hash,
            "observed_at": ev.observed_at,
        }

    @staticmethod
    def _model_dict(row: EvidenceModel) -> dict[str, Any]:
        return {
            "event_id": row.event_id,
            "source_id": row.source_id,
            "target_id": row.target_id,
            "relation": row.relation,
            "channel": row.channel,
            "source_type": row.source_type,
            "target_type": row.target_type,
            "payload_hash": row.payload_hash,
            "observed_at": row.observed_at,
            "ingested_at": row.ingested_at,
        }

    @staticmethod
    def _to_domain(row: EvidenceModel) -> EvidenceEvent:
        return EvidenceEvent(
            event_id=row.event_id,
            source_id=row.source_id,
            target_id=row.target_id,
            relation=Relation(row.relation),
            channel=EvidenceChannel(row.channel),
            observed_at=row.observed_at,
            source_type=EntityType(row.source_type) if row.source_type else None,
            target_type=EntityType(row.target_type) if row.target_type else None,
            payload_hash=row.payload_hash,
        )
