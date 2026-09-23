"""Audit log repository."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.audit_log import AuditLog
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore


class AuditRepository(RepositoryBase):
    async def append(
        self,
        *,
        principal_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> dict[str, Any]:
        record = {
            "log_id": str(uuid.uuid4()),
            "principal_id": principal_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "created_at": utcnow(),
        }
        if self.memory:
            self.memory.audit_log.append(record)
            return record

        assert self.session is not None
        self.session.add(
            AuditLog(
                log_id=record["log_id"],
                principal_id=principal_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                created_at=record["created_at"],
            )
        )
        await self.session.commit()
        return record

    async def list_entries(self, *, offset: int = 0, limit: int = 50) -> tuple[list[dict[str, Any]], int]:
        if self.memory:
            rows = sorted(self.memory.audit_log, key=lambda r: r["created_at"], reverse=True)
            total = len(rows)
            return rows[offset : offset + limit], total

        assert self.session is not None
        q = select(AuditLog).order_by(AuditLog.created_at.desc())
        result = await self.session.execute(q.offset(offset).limit(limit))
        items = [
            {
                "log_id": r.log_id,
                "principal_id": r.principal_id,
                "action": r.action,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "details": r.details,
                "ip_address": r.ip_address,
                "created_at": r.created_at,
            }
            for r in result.scalars().all()
        ]
        total = len((await self.session.execute(select(AuditLog))).scalars().all())
        return items, total
