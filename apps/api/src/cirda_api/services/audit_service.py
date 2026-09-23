"""Audit logging service."""

from __future__ import annotations

from typing import Any

from cirda_api.db.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, repo: AuditRepository) -> None:
        self.repo = repo

    async def log(
        self,
        *,
        principal_id: str | None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> dict[str, Any]:
        return await self.repo.append(
            principal_id=principal_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )

    async def list_entries(self, *, offset: int = 0, limit: int = 50) -> tuple[list[dict[str, Any]], int]:
        return await self.repo.list_entries(offset=offset, limit=limit)
