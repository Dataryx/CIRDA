"""Graph query service."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import networkx as nx

from cirda_core.domain.enums import GraphLayer
from cirda_core.graph.kernel import build_digraph
from cirda_core.version import ENGINE_VERSION

from cirda_api.db.repositories.edge import EdgeRepository
from cirda_api.db.repositories.entity import EntityRepository


class GraphService:
    def __init__(self, entity_repo: EntityRepository, edge_repo: EdgeRepository) -> None:
        self.entity_repo = entity_repo
        self.edge_repo = edge_repo

    async def get_graph_payload(
        self,
        *,
        layer: GraphLayer | None = None,
        as_of: datetime | None = None,
    ) -> dict[str, Any]:
        entities, _ = await self.entity_repo.list_entities(limit=10_000)
        edges, _ = await self.edge_repo.list_edges(
            layer=layer.value if layer == GraphLayer.CONFIRMED else None,
            as_of=as_of,
            limit=50_000,
        )
        if layer == GraphLayer.CONFIRMED:
            edges = [e for e in edges if e["layer"] == GraphLayer.CONFIRMED.value]
        elif layer == GraphLayer.POSSIBLE:
            pass  # includes confirmed + possible per INV-014 union for possible view

        node_payload = [
            {
                "entity_id": e["entity_id"],
                "entity_type": e["entity_type"],
                "name": e["name"],
                "criticality": e["criticality"],
            }
            for e in entities
        ]
        edge_payload = [
            {
                "edge_id": e["edge_id"],
                "source_id": e["source_id"],
                "target_id": e["target_id"],
                "relation": e["relation"],
                "layer": e["layer"],
                "confidence": e["confidence"],
                "necessity": e.get("necessity", "unknown"),
                "evidence_count": e.get("evidence_count", 0),
            }
            for e in edges
        ]
        return {
            "nodes": node_payload,
            "edges": edge_payload,
            "layer": layer.value if layer else "all",
            "as_of": as_of,
            "engine_version": ENGINE_VERSION,
        }

    async def build_digraph(
        self,
        layer: GraphLayer,
        *,
        as_of: datetime | None = None,
    ) -> nx.DiGraph:
        entities, _ = await self.entity_repo.list_entities(limit=10_000)
        edges_raw, _ = await self.edge_repo.list_edges(as_of=as_of, limit=50_000)
        domain_entities = [self.entity_repo.to_domain(e) for e in entities]
        domain_edges = [EdgeRepository.to_domain(e) for e in edges_raw]
        if layer == GraphLayer.CONFIRMED:
            domain_edges = [e for e in domain_edges if e.layer == GraphLayer.CONFIRMED]
            return build_digraph(domain_entities, domain_edges, layer=None)
        # POSSIBLE view = confirmed ∪ possible (INV-014).
        return build_digraph(domain_entities, domain_edges, layer=None)
