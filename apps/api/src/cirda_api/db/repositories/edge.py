"""Edge repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.edge import Edge as EdgeModel
from cirda_api.db.models.edge import EdgeChannelEvidence, EdgeVersion
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import GraphLayer, Necessity, Relation


class EdgeRepository(RepositoryBase):
    async def list_edges(
        self,
        *,
        layer: str | None = None,
        source_id: str | None = None,
        target_id: str | None = None,
        as_of: datetime | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = list(self.memory.edges.values())
            rows = self._filter_temporal(rows, as_of)
            if layer:
                rows = [r for r in rows if r["layer"] == layer]
            if source_id:
                rows = [r for r in rows if r["source_id"] == source_id]
            if target_id:
                rows = [r for r in rows if r["target_id"] == target_id]
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = select(EdgeModel)
        if layer:
            q = q.where(EdgeModel.layer == layer)
        if source_id:
            q = q.where(EdgeModel.source_id == source_id)
        if target_id:
            q = q.where(EdgeModel.target_id == target_id)
        if as_of:
            q = q.where(EdgeModel.valid_from <= as_of).where(
                (EdgeModel.valid_to.is_(None)) | (EdgeModel.valid_to > as_of)
            )
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = result.scalars().all()
        all_q = select(EdgeModel)
        if as_of:
            all_q = all_q.where(EdgeModel.valid_from <= as_of).where(
                (EdgeModel.valid_to.is_(None)) | (EdgeModel.valid_to > as_of)
            )
        total = len((await self.session.execute(all_q)).scalars().all())
        return [self._model_dict(i) for i in items], total

    async def get_edge(self, edge_id: str, *, as_of: datetime | None = None) -> dict[str, Any] | None:
        if self.memory:
            row = self.memory.edges.get(edge_id)
            if not row:
                return None
            filtered = self._filter_temporal([row], as_of)
            return filtered[0] if filtered else None

        assert self.session is not None
        row = await self.session.get(EdgeModel, edge_id)
        if not row:
            return None
        if as_of and (row.valid_from > as_of or (row.valid_to and row.valid_to <= as_of)):
            return None
        data = self._model_dict(row)
        ch_result = await self.session.execute(
            select(EdgeChannelEvidence).where(EdgeChannelEvidence.edge_id == edge_id)
        )
        data["channels"] = [
            {"channel": c.channel, "observation_count": c.observation_count, "last_observed_at": c.last_observed_at}
            for c in ch_result.scalars().all()
        ]
        return data

    async def upsert_edge(self, edge: DependencyEdge, *, valid_from: datetime | None = None) -> dict[str, Any]:
        vf = valid_from or utcnow()
        if self.memory:
            return self.memory.upsert_edge_record(edge, valid_from=vf)

        assert self.session is not None
        key = edge.edge_id or f"{edge.source_id}->{edge.target_id}:{edge.relation.value}"
        now = utcnow()
        existing = await self.session.get(EdgeModel, key)
        if existing:
            existing.layer = edge.layer.value
            existing.confidence = edge.confidence
            existing.necessity = edge.necessity.value
            existing.evidence_count = edge.evidence_count
            existing.updated_at = now
            row = existing
        else:
            row = EdgeModel(
                edge_id=key,
                source_id=edge.source_id,
                target_id=edge.target_id,
                relation=edge.relation.value,
                layer=edge.layer.value,
                confidence=edge.confidence,
                necessity=edge.necessity.value,
                evidence_count=edge.evidence_count,
                valid_from=vf,
                created_at=now,
                updated_at=now,
            )
            self.session.add(row)
        version = EdgeVersion(
            edge_id=key,
            layer=edge.layer.value,
            confidence=edge.confidence,
            snapshot={"source_id": edge.source_id, "target_id": edge.target_id},
            valid_from=vf,
            created_at=now,
        )
        self.session.add(version)
        await self.session.commit()
        return self._model_dict(row)

    async def increment_channel(self, edge_id: str, channel: str, observed_at: datetime) -> None:
        if self.memory:
            self.memory.increment_channel_evidence(edge_id, channel, observed_at)
            return

        assert self.session is not None
        result = await self.session.execute(
            select(EdgeChannelEvidence).where(
                EdgeChannelEvidence.edge_id == edge_id,
                EdgeChannelEvidence.channel == channel,
            )
        )
        row = result.scalar_one_or_none()
        if row:
            row.observation_count += 1
            row.last_observed_at = observed_at
        else:
            self.session.add(
                EdgeChannelEvidence(
                    edge_id=edge_id,
                    channel=channel,
                    observation_count=1,
                    last_observed_at=observed_at,
                )
            )
        await self.session.commit()

    @staticmethod
    def _filter_temporal(rows: list[dict[str, Any]], as_of: datetime | None) -> list[dict[str, Any]]:
        if as_of is None:
            return rows
        out: list[dict[str, Any]] = []
        for r in rows:
            vf = r.get("valid_from")
            vt = r.get("valid_to")
            if vf and vf > as_of:
                continue
            if vt and vt <= as_of:
                continue
            out.append(r)
        return out

    @staticmethod
    def _model_dict(row: EdgeModel) -> dict[str, Any]:
        return {
            "edge_id": row.edge_id,
            "source_id": row.source_id,
            "target_id": row.target_id,
            "relation": row.relation,
            "layer": row.layer,
            "confidence": row.confidence,
            "necessity": row.necessity,
            "evidence_count": row.evidence_count,
            "last_observed_at": row.last_observed_at,
            "valid_from": row.valid_from,
            "valid_to": row.valid_to,
        }

    @staticmethod
    def to_domain(record: dict[str, Any]) -> DependencyEdge:
        return DependencyEdge(
            edge_id=record["edge_id"],
            source_id=record["source_id"],
            target_id=record["target_id"],
            relation=Relation(record["relation"]),
            layer=GraphLayer(record["layer"]),
            confidence=record["confidence"],
            necessity=Necessity(record.get("necessity", "unknown")),
            evidence_count=record.get("evidence_count", 0),
            last_observed_epoch=record["last_observed_at"].timestamp()
            if record.get("last_observed_at")
            else None,
        )
