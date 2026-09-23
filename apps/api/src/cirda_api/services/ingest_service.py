"""Evidence ingest pipeline."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.enums import EvidenceChannel, GraphLayer, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.graph.layers import classify_layer
from cirda_core.inference.direction import translate_to_dependency_edge
from cirda_core.inference.fusion import ChannelObservation, fuse_channels, has_direct_evidence
from cirda_core.normalization.adapters import (
    AgentFrameworkAdapter,
    DatabaseAdapter,
    IamAdapter,
    MessagingAdapter,
    StaticAdapter,
    TraceAdapter,
)
from cirda_core.normalization.normalizer import Normalizer

from cirda_api.db.repositories.edge import EdgeRepository
from cirda_api.db.repositories.entity import EntityRepository
from cirda_api.db.repositories.evidence import EvidenceRepository
from cirda_api.ws.publisher import EventPublisher


class IngestService:
    def __init__(
        self,
        evidence_repo: EvidenceRepository,
        edge_repo: EdgeRepository,
        entity_repo: EntityRepository,
        policy: PolicyConfig,
        publisher: EventPublisher | None = None,
    ) -> None:
        self.evidence_repo = evidence_repo
        self.edge_repo = edge_repo
        self.entity_repo = entity_repo
        self.policy = policy
        self.publisher = publisher
        self.normalizer = Normalizer(
            [
                TraceAdapter(),
                DatabaseAdapter(),
                MessagingAdapter(),
                IamAdapter(),
                AgentFrameworkAdapter(),
                StaticAdapter(),
            ]
        )

    async def ingest_raw(self, raw: dict[str, Any], *, idempotency_key: str | None = None) -> dict[str, Any]:
        event = self.normalizer.normalize(raw)
        return await self.ingest_event(event, idempotency_key=idempotency_key)

    async def ingest_event(self, event: EvidenceEvent, *, idempotency_key: str | None = None) -> dict[str, Any]:
        stored, created = await self.evidence_repo.add_event(event, idempotency_key=idempotency_key)
        if not created:
            return {"event": self.evidence_repo._event_dict(stored), "created": False, "edge_updated": False}

        await self._ensure_entities(event)
        edge_updated = await self._update_edge_from_event(stored)
        if self.publisher:
            await self.publisher.publish_evidence(stored)
        return {
            "event": self.evidence_repo._event_dict(stored),
            "created": True,
            "edge_updated": edge_updated,
        }

    async def _ensure_entities(self, event: EvidenceEvent) -> None:
        for eid, etype in (
            (event.source_id, event.source_type),
            (event.target_id, event.target_type),
        ):
            existing = await self.entity_repo.get_entity(eid)
            if not existing:
                await self.entity_repo.upsert_entity(
                    entity_id=eid,
                    entity_type=etype.value if etype else "service",
                    name=eid,
                )

    async def _update_edge_from_event(self, event: EvidenceEvent) -> bool:
        now = datetime.now(timezone.utc)
        age = max(0.0, (now - event.observed_at).total_seconds())
        count = await self.evidence_repo.count_observations(
            event.source_id, event.target_id, event.channel
        )
        obs = [ChannelObservation(channel=event.channel, count=count, age_seconds=age)]
        confidence = fuse_channels(obs)
        layer = classify_layer(confidence, has_direct_evidence(obs), self.policy)
        if layer is None:
            return False

        dep_edge = translate_to_dependency_edge(
            actor_id=event.source_id,
            counterpart_id=event.target_id,
            relation=event.relation,
            layer=layer,
            confidence=confidence,
            evidence_count=count,
            last_observed_epoch=event.observed_at.timestamp(),
        )
        record = await self.edge_repo.upsert_edge(dep_edge, valid_from=event.observed_at)
        await self.edge_repo.increment_channel(record["edge_id"], event.channel.value, event.observed_at)
        return True
