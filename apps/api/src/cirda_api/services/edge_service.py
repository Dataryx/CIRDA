"""Edge query, annotation, and necessity-hint service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_core.domain.enums import Necessity
from cirda_core.graph.kernel import build_digraph
from cirda_core.graph.necessity_suggester import suggest_necessity

from cirda_api.db.repositories.edge import EdgeRepository
from cirda_api.db.repositories.entity import EntityRepository
from cirda_api.db.repositories.evidence import EvidenceRepository
from cirda_api.services.policy import build_policy
from cirda_api.settings import Settings


class EdgeService:
    def __init__(
        self,
        edge_repo: EdgeRepository,
        evidence_repo: EvidenceRepository,
        entity_repo: EntityRepository,
        settings: Settings,
    ) -> None:
        self.edge_repo = edge_repo
        self.evidence_repo = evidence_repo
        self.entity_repo = entity_repo
        self.settings = settings

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

    async def update_necessity(self, edge_id: str, necessity: str) -> dict[str, Any] | None:
        try:
            parsed = Necessity(necessity)
        except ValueError as exc:
            raise ValueError(f"invalid necessity: {necessity}") from exc
        return await self.edge_repo.update_necessity(edge_id, parsed)

    async def necessity_suggestions(
        self,
        source_id: str,
        *,
        as_of: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Suggest-only necessity hints for UNKNOWN edges under source_id."""
        entities, _ = await self.entity_repo.list_entities(limit=10_000)
        edges_raw, _ = await self.edge_repo.list_edges(as_of=as_of, limit=50_000)
        domain_entities = [self.entity_repo.to_domain(e) for e in entities]
        # Include confirmed ∪ possible (full estate view for hints).
        domain_edges = [EdgeRepository.to_domain(e) for e in edges_raw]
        graph = build_digraph(domain_entities, domain_edges, layer=None)
        policy = build_policy(self.settings)
        hints = suggest_necessity(
            graph,
            source_id,
            criticality_threshold=policy.critical_threshold,
        )
        return [
            {
                "edge_id": h.edge_id,
                "source_id": h.source_id,
                "target_id": h.target_id,
                "current_necessity": h.current_necessity,
                "suggested_necessity": h.suggested_necessity,
                "confidence": h.confidence,
                "rationale": h.rationale,
                "signals": h.signals,
            }
            for h in hints
        ]

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
