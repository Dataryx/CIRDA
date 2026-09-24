"""Decision repository (immutable records)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.json_safe import json_safe
from cirda_api.db.models.decision import Decision as DecisionModel
from cirda_api.db.models.decision import DecisionPath, RunbookExecution
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore


class DecisionRepository(RepositoryBase):
    async def create(self, record: dict[str, Any]) -> dict[str, Any]:
        if self.memory:
            return self.memory.create_decision(record)

        assert self.session is not None
        now = utcnow()
        row = DecisionModel(
            decision_id=record["decision_id"],
            entity_id=record["entity_id"],
            verdict=record["verdict"],
            coverage=record["coverage"],
            truncated=record.get("truncated", False),
            reason_codes=json_safe(record.get("reason_codes", [])),
            rationale=json_safe(record.get("rationale", {})),
            as_of=record["as_of"],
            engine_version=record["engine_version"],
            change_type=record.get("change_type"),
            supersedes_id=record.get("supersedes_id"),
            created_at=now,
            created_by=record.get("created_by"),
        )
        self.session.add(row)
        for path in record.get("paths", []):
            self.session.add(
                DecisionPath(
                    decision_id=record["decision_id"],
                    path_nodes=path["path_nodes"],
                    path_confidence=path.get("path_confidence", 0.0),
                    is_critical_path=path.get("is_critical_path", False),
                )
            )
        await self.session.commit()
        return await self.get(record["decision_id"]) or record

    async def get(self, decision_id: str) -> dict[str, Any] | None:
        if self.memory:
            return self.memory.decisions.get(decision_id)

        assert self.session is not None
        row = await self.session.get(DecisionModel, decision_id)
        if not row:
            return None
        paths = (
            await self.session.execute(select(DecisionPath).where(DecisionPath.decision_id == decision_id))
        ).scalars().all()
        return {
            "decision_id": row.decision_id,
            "entity_id": row.entity_id,
            "verdict": row.verdict,
            "coverage": row.coverage,
            "truncated": row.truncated,
            "reason_codes": row.reason_codes,
            "rationale": row.rationale,
            "as_of": row.as_of,
            "engine_version": row.engine_version,
            "change_type": row.change_type,
            "supersedes_id": row.supersedes_id,
            "superseded_by_id": row.superseded_by_id,
            "created_at": row.created_at,
            "created_by": row.created_by,
            "paths": [
                {
                    "path_id": p.path_id,
                    "path_nodes": p.path_nodes,
                    "path_confidence": p.path_confidence,
                    "is_critical_path": p.is_critical_path,
                }
                for p in paths
            ],
        }

    async def list_for_entity(
        self,
        entity_id: str,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = [d for d in self.memory.decisions.values() if d["entity_id"] == entity_id]
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = select(DecisionModel).where(DecisionModel.entity_id == entity_id).order_by(DecisionModel.created_at.desc())
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = result.scalars().all()
        all_rows = (await self.session.execute(select(DecisionModel).where(DecisionModel.entity_id == entity_id))).scalars().all()
        return [await self.get(i.decision_id) for i in items if i], len(all_rows)  # type: ignore[misc]

    async def mark_superseded(self, old_id: str, new_id: str) -> None:
        if self.memory:
            self.memory.link_supersedes(new_id, old_id)
            return

        assert self.session is not None
        old = await self.session.get(DecisionModel, old_id)
        new = await self.session.get(DecisionModel, new_id)
        if old:
            old.superseded_by_id = new_id
        if new:
            new.supersedes_id = old_id
        await self.session.commit()
