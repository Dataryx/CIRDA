"""Edge query service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_api.db.repositories.edge import EdgeRepository
from cirda_api.db.repositories.evidence import EvidenceRepository


class EdgeService:
    def __init__(self, edge_repo: EdgeRepository, evidence_repo: EvidenceRepository) -> None:
        self.edge_repo = edge_repo
        self.evidence_repo = evidence_repo

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
        return await self.edge_repo.list_edges(
            layer=layer,
            source_id=source_id,
            target_id=target_id,
            as_of=as_of,
            offset=offset,
            limit=limit,
        )

    async def get_edge(self, edge_id: str, *, as_of: datetime | None = None) -> dict[str, Any] | None:
        return await self.edge_repo.get_edge(edge_id, as_of=as_of)

    async def edge_evidence(self, edge_id: str, *, limit: int = 50) -> list[dict[str, Any]]:
        edge = await self.edge_repo.get_edge(edge_id)
        if not edge:
            return []
        events, _ = await self.evidence_repo.list_events(
            source_id=edge["source_id"],
            target_id=edge["target_id"],
            limit=limit,
        )
        return events
