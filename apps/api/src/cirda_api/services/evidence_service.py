"""Evidence query service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_api.db.repositories.evidence import EvidenceRepository


class EvidenceService:
    def __init__(self, repo: EvidenceRepository) -> None:
        self.repo = repo

    async def get_event(self, event_id: str) -> dict[str, Any] | None:
        return await self.repo.get_event(event_id)

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
        return await self.repo.list_events(
            source_id=source_id,
            target_id=target_id,
            channel=channel,
            as_of=as_of,
            offset=offset,
            limit=limit,
        )
