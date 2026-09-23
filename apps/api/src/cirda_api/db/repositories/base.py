"""Repository base helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from cirda_api.memory.store import MemoryStore


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RepositoryBase:
    def __init__(self, session: AsyncSession | None = None, memory: MemoryStore | None = None) -> None:
        self.session = session
        self.memory = memory
        if session is None and memory is None:
            raise ValueError("session or memory required")

    @property
    def is_memory(self) -> bool:
        return self.memory is not None
