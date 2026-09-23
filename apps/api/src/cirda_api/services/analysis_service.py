"""Analysis service (blast radius, reachability)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_core.analysis.blast_radius import compute_blast_radius
from cirda_core.domain.enums import Criticality, GraphLayer
from cirda_core.graph.reachability import descendants_within_depth

from cirda_api.db.repositories.entity import EntityRepository
from cirda_api.services.graph_service import GraphService
from cirda_api.services.policy import build_policy
from cirda_api.settings import Settings


class AnalysisService:
    def __init__(self, graph_service: GraphService, entity_repo: EntityRepository, settings: Settings) -> None:
        self.graph_service = graph_service
        self.entity_repo = entity_repo
        self.settings = settings

    async def blast_radius(
        self,
        source_id: str,
        *,
        as_of: datetime | None = None,
        max_depth: int | None = None,
        max_nodes: int | None = None,
    ) -> dict[str, Any]:
        g_p = await self.graph_service.build_digraph(GraphLayer.POSSIBLE, as_of=as_of)
        policy = build_policy(self.settings)
        result = compute_blast_radius(
            g_p,
            source_id,
            criticality_threshold=policy.critical_threshold,
            max_depth=max_depth,
            max_nodes=max_nodes,
        )
        return {
            "source_id": result.source_id,
            "layer": GraphLayer.POSSIBLE.value,
            "all_reachable": sorted(result.all_reachable),
            "critical_reachable": sorted(result.critical_reachable),
            "truncated": result.truncated,
            "as_of": as_of,
        }

    async def reachability(
        self,
        source_id: str,
        *,
        as_of: datetime | None = None,
        max_depth: int | None = None,
    ) -> dict[str, Any]:
        g_p = await self.graph_service.build_digraph(GraphLayer.POSSIBLE, as_of=as_of)
        result = descendants_within_depth(g_p, source_id, max_depth)
        return {
            "source_id": source_id,
            "layer": GraphLayer.POSSIBLE.value,
            "reachable": sorted(result.reachable),
            "truncated": result.truncated,
            "as_of": as_of,
        }
