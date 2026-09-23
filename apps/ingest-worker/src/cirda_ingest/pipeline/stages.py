"""Pipeline stages: normalize -> resolve -> candidate -> fuse -> persist."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import structlog

from cirda_core.config.policy import PolicyConfig
from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.enums import EvidenceChannel
from cirda_core.domain.errors import NaiveDatetimeError
from cirda_core.domain.event import EvidenceEvent
from cirda_core.graph.layers import classify_layer
from cirda_core.inference.candidate_generator import CandidatePair, generate_candidate_edge
from cirda_core.inference.direction import translate_to_dependency_edge
from cirda_core.inference.fusion import ChannelObservation, fuse_channels, has_direct_evidence
from cirda_core.normalization.adapters import ALL_ADAPTERS
from cirda_core.normalization.normalizer import Normalizer
from cirda_core.ports.clock import Clock, SystemClock
from cirda_core.resolution.entity_resolver import EntityResolver

from cirda_ingest.pipeline.dead_letter import PermanentIngestError
from cirda_ingest.sinks.metrics_sink import MetricsSink
from cirda_ingest.sinks.postgres_sink import PersistItem, PersistResult, PostgresSink

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class InboundMessage:
    """Raw event from a consumer with checkpoint metadata."""

    raw: dict[str, Any]
    message_id: str
    source: str
    idempotency_key: str | None = None
    topic: str | None = None
    partition: int | None = None
    offset: int | None = None


@dataclass
class PipelineItem:
    """Mutable state flowing through pipeline stages."""

    message: InboundMessage
    raw: dict[str, Any]
    event: EvidenceEvent | None = None
    resolved_source: str | None = None
    resolved_target: str | None = None
    candidate_edge: DependencyEdge | None = None
    fused_edge: DependencyEdge | None = None
    permanent_error: PermanentIngestError | None = None
    channel_counts: dict[EvidenceChannel, int] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineBatchResult:
    persist: PersistResult
    permanent_failures: list[PipelineItem]
    processed: int


class IngestPipeline:
    """
    Multi-stage ingest pipeline.

    R4: incremental per-event edge updates — never rebuilds the full graph.
    INV-004: idempotent persistence keyed by event_id at the sink.
    """

    def __init__(
        self,
        sink: PostgresSink,
        *,
        policy: PolicyConfig | None = None,
        clock: Clock | None = None,
        resolver: EntityResolver | None = None,
        metrics: MetricsSink | None = None,
    ) -> None:
        self._sink = sink
        self._policy = policy or PolicyConfig()
        self._clock = clock or SystemClock()
        self._resolver = resolver or EntityResolver()
        self._metrics = metrics
        self._normalizer = Normalizer(list(ALL_ADAPTERS))

    @property
    def resolver(self) -> EntityResolver:
        return self._resolver

    async def process_batch(self, messages: list[InboundMessage]) -> PipelineBatchResult:
        items = [PipelineItem(message=m, raw=m.raw) for m in messages]
        permanent_failures: list[PipelineItem] = []

        for item in items:
            self._stage_normalize(item)
            if item.permanent_error:
                permanent_failures.append(item)
                continue
            self._stage_resolve(item)
            await self._stage_candidate(item)
            await self._stage_fuse(item)

        persist_items: list[PersistItem] = []
        for item in items:
            if item.permanent_error or item.event is None:
                continue
            persist_items.append(
                PersistItem(
                    event=item.event,
                    edge=item.fused_edge,
                    idempotency_key=item.message.idempotency_key,
                    message_id=item.message.message_id,
                )
            )

        persist_result = await self._stage_persist(persist_items)
        return PipelineBatchResult(
            persist=persist_result,
            permanent_failures=permanent_failures,
            processed=len(messages),
        )

    def _stage_normalize(self, item: PipelineItem) -> None:
        try:
            item.event = self._normalizer.normalize(item.raw)
        except (ValueError, NaiveDatetimeError, KeyError, TypeError) as exc:
            item.permanent_error = PermanentIngestError(str(exc))
            logger.debug("normalize_failed", error=str(exc), source=item.message.source)

    def _stage_resolve(self, item: PipelineItem) -> None:
        assert item.event is not None
        event = item.event
        item.resolved_source = self._resolver.resolve_or_passthrough(event.source_id)
        item.resolved_target = self._resolver.resolve_or_passthrough(event.target_id)
        if item.resolved_source != event.source_id or item.resolved_target != event.target_id:
            item.event = EvidenceEvent(
                event_id=event.event_id,
                source_id=item.resolved_source,
                target_id=item.resolved_target,
                relation=event.relation,
                channel=event.channel,
                observed_at=event.observed_at,
                source_type=event.source_type,
                target_type=event.target_type,
                payload_hash=event.payload_hash,
            )

    async def _stage_candidate(self, item: PipelineItem) -> None:
        """Generate candidate edge for this event only (no full-graph rebuild)."""
        assert item.event is not None
        event = item.event
        pair = CandidatePair(
            actor_id=event.source_id,
            counterpart_id=event.target_id,
            relation=event.relation,
            channel_counts={event.channel: 1},
            last_observed=event.observed_at,
        )
        item.candidate_edge = generate_candidate_edge(pair, self._clock, self._policy)

    async def _stage_fuse(self, item: PipelineItem) -> None:
        """
        Fuse channel observations using stored counts for this edge pair.

        Reads existing observation counts from the sink instead of rebuilding graph state.
        """
        assert item.event is not None
        event = item.event
        stored_count = await self._sink.count_observations(event.source_id, event.target_id, event.channel)
        item.channel_counts[event.channel] = stored_count + 1

        now = self._clock.now()
        age_seconds = max(0.0, (now - event.observed_at).total_seconds())
        observations = [
            ChannelObservation(channel=ch, count=cnt, age_seconds=age_seconds)
            for ch, cnt in item.channel_counts.items()
            if cnt > 0
        ]
        if not observations:
            item.fused_edge = None
            return

        confidence = fuse_channels(observations)
        layer = classify_layer(confidence, has_direct_evidence(observations), self._policy)
        if layer is None:
            item.fused_edge = None
            return

        item.fused_edge = translate_to_dependency_edge(
            actor_id=event.source_id,
            counterpart_id=event.target_id,
            relation=event.relation,
            layer=layer,
            confidence=confidence,
            evidence_count=sum(item.channel_counts.values()),
            last_observed_epoch=event.observed_at.timestamp(),
        )

    async def _stage_persist(self, items: list[PersistItem]) -> PersistResult:
        if not items:
            return PersistResult()
        result = await self._sink.persist_batch(items)
        if self._metrics:
            self._metrics.record_persist(
                created=len(result.created_event_ids),
                deduped=len(result.deduped_event_ids),
                edges=len(result.updated_edge_ids),
            )
        return result


def sample_trace_raw(
    event_id: str,
    *,
    source_id: str = "svc-a",
    target_id: str = "svc-b",
    observed_at: datetime | None = None,
) -> dict[str, Any]:
    """Helper for tests and dev publish."""
    ts = observed_at or datetime.now(timezone.utc)
    return {
        "source": "trace",
        "event_id": event_id,
        "source_id": source_id,
        "target_id": target_id,
        "relation": "calls",
        "observed_at": ts.isoformat(),
    }
