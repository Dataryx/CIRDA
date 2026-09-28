"""Decision repository (immutable records + runbook executions)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.json_safe import json_safe
from cirda_api.db.models.decision import Decision as DecisionModel
from cirda_api.db.models.decision import DecisionPath, RunbookExecution
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore

_ALLOWED_STATUS = frozenset({"pending", "in_progress", "completed"})
_TRANSITIONS: dict[str, frozenset[str]] = {
    "pending": frozenset({"in_progress", "completed"}),
    "in_progress": frozenset({"completed"}),
    "completed": frozenset(),
}


class DecisionRepository(RepositoryBase):
    async def create(self, record: dict[str, Any]) -> dict[str, Any]:
        if self.memory:
            return self.memory.create_decision(record)

        assert self.session is not None
        now = utcnow()
        row = DecisionModel(
            decision_id=record["decision_id"],
            tenant_id=self.tenant_id,
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
        executions = record.get("runbook_executions")
        if executions is None:
            executions = []
            for action in (record.get("rationale") or {}).get("suggested_runbook") or []:
                executions.append(
                    {
                        "execution_id": str(uuid.uuid4()),
                        "stage": action["stage"],
                        "status": "pending",
                        "notes": None,
                        "description": action.get("description"),
                    }
                )
        for exe in executions:
            self.session.add(
                RunbookExecution(
                    execution_id=exe.get("execution_id") or str(uuid.uuid4()),
                    decision_id=record["decision_id"],
                    stage=exe["stage"],
                    status=exe.get("status", "pending"),
                    notes=exe.get("notes"),
                )
            )
        await self.session.commit()
        return await self.get(record["decision_id"]) or record

    async def get(self, decision_id: str) -> dict[str, Any] | None:
        if self.memory:
            return self.memory.get_decision(decision_id)

        assert self.session is not None
        result = await self.session.execute(
            select(DecisionModel).where(
                DecisionModel.decision_id == decision_id,
                DecisionModel.tenant_id == self.tenant_id,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            return None
        paths = (
            await self.session.execute(select(DecisionPath).where(DecisionPath.decision_id == decision_id))
        ).scalars().all()
        executions = (
            await self.session.execute(
                select(RunbookExecution).where(RunbookExecution.decision_id == decision_id)
            )
        ).scalars().all()
        return {
            "decision_id": row.decision_id,
            "entity_id": row.entity_id,
            "tenant_id": row.tenant_id,
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
            "runbook_executions": [
                {
                    "execution_id": e.execution_id,
                    "stage": e.stage,
                    "status": e.status,
                    "started_at": e.started_at,
                    "completed_at": e.completed_at,
                    "notes": e.notes,
                }
                for e in executions
            ],
        }

    async def list_runbook_executions(self, decision_id: str) -> list[dict[str, Any]]:
        if self.memory:
            return self.memory.list_runbook_executions(decision_id)

        assert self.session is not None
        rows = (
            await self.session.execute(
                select(RunbookExecution).where(RunbookExecution.decision_id == decision_id)
            )
        ).scalars().all()
        return [
            {
                "execution_id": e.execution_id,
                "decision_id": decision_id,
                "stage": e.stage,
                "status": e.status,
                "started_at": e.started_at,
                "completed_at": e.completed_at,
                "notes": e.notes,
            }
            for e in rows
        ]

    async def update_runbook_execution(
        self,
        decision_id: str,
        execution_id: str,
        *,
        status: str,
        notes: str | None = None,
    ) -> dict[str, Any] | None:
        if status not in _ALLOWED_STATUS:
            raise ValueError(f"invalid runbook status: {status}")

        if self.memory:
            rows = self.memory.list_runbook_executions(decision_id)
            current = next((r for r in rows if r["execution_id"] == execution_id), None)
            if not current:
                return None
            allowed = _TRANSITIONS.get(current["status"], frozenset())
            if status != current["status"] and status not in allowed:
                raise ValueError(
                    f"cannot transition runbook stage from {current['status']} to {status}"
                )
            return self.memory.update_runbook_execution(
                decision_id, execution_id, status=status, notes=notes
            )

        assert self.session is not None
        row = await self.session.get(RunbookExecution, execution_id)
        if not row or row.decision_id != decision_id:
            return None
        allowed = _TRANSITIONS.get(row.status, frozenset())
        if status != row.status and status not in allowed:
            raise ValueError(f"cannot transition runbook stage from {row.status} to {status}")
        now = utcnow()
        row.status = status
        if notes is not None:
            row.notes = notes
        if status == "in_progress" and row.started_at is None:
            row.started_at = now
        if status == "completed":
            if row.started_at is None:
                row.started_at = now
            row.completed_at = now
        await self.session.commit()
        return {
            "execution_id": row.execution_id,
            "decision_id": decision_id,
            "stage": row.stage,
            "status": row.status,
            "started_at": row.started_at,
            "completed_at": row.completed_at,
            "notes": row.notes,
        }

    async def list_for_entity(
        self,
        entity_id: str,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = [d for d in self.memory.iter_tenant_decisions() if d["entity_id"] == entity_id]
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = (
            select(DecisionModel)
            .where(
                DecisionModel.tenant_id == self.tenant_id,
                DecisionModel.entity_id == entity_id,
            )
            .order_by(DecisionModel.created_at.desc())
        )
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = result.scalars().all()
        all_rows = (
            await self.session.execute(
                select(DecisionModel).where(
                    DecisionModel.tenant_id == self.tenant_id,
                    DecisionModel.entity_id == entity_id,
                )
            )
        ).scalars().all()
        return [await self.get(i.decision_id) for i in items if i], len(all_rows)  # type: ignore[misc]

    async def mark_superseded(self, old_id: str, new_id: str) -> None:
        if self.memory:
            self.memory.link_supersedes(new_id, old_id)
            return

        assert self.session is not None
        old = (
            await self.session.execute(
                select(DecisionModel).where(
                    DecisionModel.decision_id == old_id,
                    DecisionModel.tenant_id == self.tenant_id,
                )
            )
        ).scalar_one_or_none()
        new = (
            await self.session.execute(
                select(DecisionModel).where(
                    DecisionModel.decision_id == new_id,
                    DecisionModel.tenant_id == self.tenant_id,
                )
            )
        ).scalar_one_or_none()
        if old:
            old.superseded_by_id = new_id
        if new:
            new.supersedes_id = old_id
        await self.session.commit()
