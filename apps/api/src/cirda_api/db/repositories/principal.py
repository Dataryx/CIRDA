"""Principal repository."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.db.models.principal import Principal
from cirda_api.db.repositories.base import RepositoryBase, utcnow
from cirda_api.memory.store import MemoryStore


class PrincipalRepository(RepositoryBase):
    async def get_by_subject(self, subject: str) -> dict[str, Any] | None:
        if self.memory:
            for p in self.memory.principals.values():
                if p["subject"] == subject:
                    return p
            return None

        assert self.session is not None
        result = await self.session.execute(select(Principal).where(Principal.subject == subject))
        row = result.scalar_one_or_none()
        return self._dict(row) if row else None

    async def get_by_api_key_hash(self, api_key_hash: str) -> dict[str, Any] | None:
        if self.memory:
            for p in self.memory.principals.values():
                if p.get("api_key_hash") == api_key_hash:
                    return p
            return None

        assert self.session is not None
        result = await self.session.execute(select(Principal).where(Principal.api_key_hash == api_key_hash))
        row = result.scalar_one_or_none()
        return self._dict(row) if row else None

    @staticmethod
    def _dict(row: Principal) -> dict[str, Any]:
        return {
            "principal_id": row.principal_id,
            "subject": row.subject,
            "roles": row.roles,
            "api_key_hash": row.api_key_hash,
            "is_active": row.is_active,
        }
