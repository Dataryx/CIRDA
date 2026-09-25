"""Async PostgreSQL / SQLite sink aligned with CIRDA API schema."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EntityType, EvidenceChannel, GraphLayer, Necessity, Relation
from cirda_core.domain.event import EvidenceEvent


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


TzDateTime = DateTime(timezone=True)


class Base(DeclarativeBase):
    pass


class EntityRow(Base):
    __tablename__ = "entities"

    entity_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    criticality: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    created_at: Mapped[datetime] = mapped_column(TzDateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TzDateTime, nullable=False)


class EvidenceRow(Base):
    __tablename__ = "evidence_events"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_evidence_idempotency"),)

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    relation: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    source_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payload_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(TzDateTime, nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(TzDateTime, nullable=False)


class EdgeRow(Base):
    __tablename__ = "edges"

    edge_id: Mapped[str] = mapped_column(String(256), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(128), ForeignKey("entities.entity_id"), index=True)
    target_id: Mapped[str] = mapped_column(String(128), ForeignKey("entities.entity_id"), index=True)
    relation: Mapped[str] = mapped_column(String(32), nullable=False)
    layer: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    necessity: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_observed_at: Mapped[datetime | None] = mapped_column(TzDateTime, nullable=True)
    valid_from: Mapped[datetime] = mapped_column(TzDateTime, nullable=False)
    valid_to: Mapped[datetime | None] = mapped_column(TzDateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TzDateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TzDateTime, nullable=False)


class EdgeChannelRow(Base):
    __tablename__ = "edge_channel_evidence"
    __table_args__ = (UniqueConstraint("edge_id", "channel", name="uq_edge_channel"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    edge_id: Mapped[str] = mapped_column(String(256), ForeignKey("edges.edge_id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    observation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_observed_at: Mapped[datetime | None] = mapped_column(TzDateTime, nullable=True)


@dataclass(slots=True)
class PersistItem:
    """One pipeline item ready for durable write."""

    event: EvidenceEvent
    edge: DependencyEdge | None
    idempotency_key: str | None = None
    message_id: str = ""


@dataclass(slots=True)
class PersistResult:
    """Outcome of a durable batch write."""

    created_event_ids: list[str] = field(default_factory=list)
    deduped_event_ids: list[str] = field(default_factory=list)
    updated_edge_ids: list[str] = field(default_factory=list)
    durable_message_ids: list[str] = field(default_factory=list)


@dataclass
class _MemoryTables:
    evidence: dict[str, EvidenceEvent] = field(default_factory=dict)
    idempotency_index: dict[str, str] = field(default_factory=dict)
    entities: set[str] = field(default_factory=set)
    edges: dict[str, dict[str, Any]] = field(default_factory=dict)
    channel_counts: dict[tuple[str, str], int] = field(default_factory=dict)


class PostgresSink:
    """Idempotent evidence and incremental edge persistence (INV-004)."""

    def __init__(self, database_url: str, *, memory_mode: bool = False) -> None:
        self._memory_mode = memory_mode
        self._memory = _MemoryTables() if memory_mode else None
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        if not memory_mode:
            self._engine = create_async_engine(database_url, pool_pre_ping=True)
            self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def initialize(self) -> None:
        if self._engine is not None:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()

    async def persist_batch(self, items: list[PersistItem]) -> PersistResult:
        if self._memory is not None:
            return self._persist_memory(items)

        assert self._session_factory is not None
        result = PersistResult()
        async with self._session_factory() as session:
            async with session.begin():
                for item in items:
                    created = await self._persist_one(session, item, result)
                    if created or item.event.event_id in result.deduped_event_ids:
                        if item.message_id:
                            result.durable_message_ids.append(item.message_id)
        return result

    async def count_observations(
        self,
        source_id: str,
        target_id: str,
        channel: EvidenceChannel,
    ) -> int:
        if self._memory is not None:
            count = 0
            for ev in self._memory.evidence.values():
                if ev.source_id == source_id and ev.target_id == target_id and ev.channel == channel:
                    count += 1
            return count

        assert self._session_factory is not None
        async with self._session_factory() as session:
            q = select(EvidenceRow).where(
                EvidenceRow.source_id == source_id,
                EvidenceRow.target_id == target_id,
                EvidenceRow.channel == channel.value,
            )
            rows = (await session.execute(q)).scalars().all()
            return len(rows)

    async def _persist_one(
        self,
        session: AsyncSession,
        item: PersistItem,
        result: PersistResult,
    ) -> bool:
        event = item.event
        if item.idempotency_key:
            existing = await session.execute(
                select(EvidenceRow).where(EvidenceRow.idempotency_key == item.idempotency_key)
            )
            row = existing.scalar_one_or_none()
            if row:
                result.deduped_event_ids.append(row.event_id)
                return False

        existing_event = await session.get(EvidenceRow, event.event_id)
        if existing_event:
            result.deduped_event_ids.append(event.event_id)
            return False

        now = utcnow()
        await self._ensure_entity(session, event.source_id, event.source_type, now)
        await self._ensure_entity(session, event.target_id, event.target_type, now)

        session.add(
            EvidenceRow(
                event_id=event.event_id,
                idempotency_key=item.idempotency_key,
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
        )
        result.created_event_ids.append(event.event_id)

        if item.edge is not None:
            edge_id = await self._upsert_edge(session, item.edge, valid_from=event.observed_at)
            await self._increment_channel(session, edge_id, event.channel.value, event.observed_at)
            result.updated_edge_ids.append(edge_id)

        return True

    async def _ensure_entity(
        self,
        session: AsyncSession,
        entity_id: str,
        entity_type: EntityType | None,
        now: datetime,
    ) -> None:
        existing = await session.get(EntityRow, entity_id)
        if existing:
            return
        session.add(
            EntityRow(
                entity_id=entity_id,
                entity_type=entity_type.value if entity_type else "service",
                name=entity_id,
                criticality="unknown",
                created_at=now,
                updated_at=now,
            )
        )

    async def _upsert_edge(
        self,
        session: AsyncSession,
        edge: DependencyEdge,
        *,
        valid_from: datetime,
    ) -> str:
        key = edge.edge_id or f"{edge.source_id}->{edge.target_id}:{edge.relation.value}"
        now = utcnow()
        existing = await session.get(EdgeRow, key)
        if existing:
            existing.layer = edge.layer.value
            existing.confidence = edge.confidence
            existing.necessity = edge.necessity.value
            existing.evidence_count = edge.evidence_count
            existing.last_observed_at = valid_from
            existing.updated_at = now
        else:
            session.add(
                EdgeRow(
                    edge_id=key,
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    relation=edge.relation.value,
                    layer=edge.layer.value,
                    confidence=edge.confidence,
                    necessity=edge.necessity.value,
                    evidence_count=edge.evidence_count,
                    last_observed_at=valid_from,
                    valid_from=valid_from,
                    created_at=now,
                    updated_at=now,
                )
            )
        return key

    async def _increment_channel(
        self,
        session: AsyncSession,
        edge_id: str,
        channel: str,
        observed_at: datetime,
    ) -> None:
        result = await session.execute(
            select(EdgeChannelRow).where(
                EdgeChannelRow.edge_id == edge_id,
                EdgeChannelRow.channel == channel,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.observation_count += 1
            row.last_observed_at = observed_at
        else:
            session.add(
                EdgeChannelRow(
                    edge_id=edge_id,
                    channel=channel,
                    observation_count=1,
                    last_observed_at=observed_at,
                )
            )

    def _persist_memory(self, items: list[PersistItem]) -> PersistResult:
        assert self._memory is not None
        result = PersistResult()
        for item in items:
            event = item.event
            if item.idempotency_key and item.idempotency_key in self._memory.idempotency_index:
                existing_id = self._memory.idempotency_index[item.idempotency_key]
                result.deduped_event_ids.append(existing_id)
                if item.message_id:
                    result.durable_message_ids.append(item.message_id)
                continue
            if event.event_id in self._memory.evidence:
                result.deduped_event_ids.append(event.event_id)
                if item.message_id:
                    result.durable_message_ids.append(item.message_id)
                continue

            self._memory.evidence[event.event_id] = event
            if item.idempotency_key:
                self._memory.idempotency_index[item.idempotency_key] = event.event_id
            self._memory.entities.add(event.source_id)
            self._memory.entities.add(event.target_id)
            result.created_event_ids.append(event.event_id)

            if item.edge is not None:
                key = item.edge.edge_id or f"{item.edge.source_id}->{item.edge.target_id}:{item.edge.relation.value}"
                self._memory.edges[key] = {
                    "edge_id": key,
                    "layer": item.edge.layer.value,
                    "confidence": item.edge.confidence,
                }
                ch_key = (key, event.channel.value)
                self._memory.channel_counts[ch_key] = self._memory.channel_counts.get(ch_key, 0) + 1
                result.updated_edge_ids.append(key)

            if item.message_id:
                result.durable_message_ids.append(item.message_id)

        return result
