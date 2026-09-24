"""Thread-safe in-memory store implementing graph and evidence ports."""

from __future__ import annotations

import threading
import uuid
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from cirda_core.domain.edge import DependencyEdge
from cirda_core.domain.entity import Entity
from cirda_core.domain.enums import (
    Criticality,
    EntityType,
    EvidenceChannel,
    GraphLayer,
    Necessity,
    Relation,
    Verdict,
)
from cirda_core.domain.event import EvidenceEvent


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class MemoryStore:
    """In-memory repository backing for dev/test without PostgreSQL."""

    entities: dict[str, Entity] = field(default_factory=dict)
    aliases: dict[str, list[tuple[str, str | None]]] = field(default_factory=dict)
    edges: dict[str, dict[str, Any]] = field(default_factory=dict)
    edge_channel_evidence: dict[str, dict[str, dict[str, Any]]] = field(default_factory=dict)
    edge_versions: list[dict[str, Any]] = field(default_factory=list)
    evidence_events: dict[str, EvidenceEvent] = field(default_factory=dict)
    idempotency_index: dict[str, str] = field(default_factory=dict)
    decisions: dict[str, dict[str, Any]] = field(default_factory=dict)
    decision_paths: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    runbook_executions: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    coverage_snapshots: list[dict[str, Any]] = field(default_factory=list)
    channel_health: dict[str, dict[str, Any]] = field(default_factory=dict)
    calibration_profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    benchmark_runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    benchmark_results: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    principals: dict[str, dict[str, Any]] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def upsert_entity_record(
        self,
        *,
        entity_id: str,
        entity_type: str,
        name: str,
        criticality: str = "unknown",
        metadata: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        ts = now or _utcnow()
        with self._lock:
            existing = self.entities.get(entity_id)
            entity = Entity(
                entity_id=entity_id,
                entity_type=EntityType(entity_type),
                name=name,
                criticality=Criticality(criticality),
            )
            self.entities[entity_id] = entity
            record = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "name": name,
                "criticality": criticality,
                "metadata": metadata or {},
                "created_at": ts if existing is None else getattr(existing, "_created_at", ts),
                "updated_at": ts,
            }
            return record

    def add_alias(self, entity_id: str, alias: str, source: str | None = None) -> None:
        with self._lock:
            self.aliases.setdefault(entity_id, []).append((alias, source))

    def add_evidence(self, event: EvidenceEvent, idempotency_key: str | None = None) -> tuple[EvidenceEvent, bool]:
        with self._lock:
            if idempotency_key and idempotency_key in self.idempotency_index:
                existing_id = self.idempotency_index[idempotency_key]
                return self.evidence_events[existing_id], False
            if event.event_id in self.evidence_events:
                return self.evidence_events[event.event_id], False
            self.evidence_events[event.event_id] = event
            if idempotency_key:
                self.idempotency_index[idempotency_key] = event.event_id
            return event, True

    def upsert_edge_record(self, edge: DependencyEdge, *, valid_from: datetime, valid_to: datetime | None = None) -> dict[str, Any]:
        key = edge.edge_id or f"{edge.source_id}->{edge.target_id}:{edge.relation.value}"
        now = _utcnow()
        record = {
            "edge_id": key,
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "relation": edge.relation.value,
            "layer": edge.layer.value,
            "confidence": edge.confidence,
            "necessity": edge.necessity.value,
            "evidence_count": edge.evidence_count,
            "last_observed_at": datetime.fromtimestamp(edge.last_observed_epoch, tz=timezone.utc)
            if edge.last_observed_epoch
            else now,
            "valid_from": valid_from,
            "valid_to": valid_to,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self.edges[key] = record
            ch = self.edge_channel_evidence.setdefault(key, {})
            return record

    def increment_channel_evidence(self, edge_id: str, channel: str, observed_at: datetime) -> None:
        with self._lock:
            ch_map = self.edge_channel_evidence.setdefault(edge_id, {})
            entry = ch_map.get(channel, {"observation_count": 0, "last_observed_at": observed_at})
            entry["observation_count"] += 1
            entry["last_observed_at"] = observed_at
            ch_map[channel] = entry

    def create_decision(self, record: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            decision_id = record.get("decision_id") or str(uuid.uuid4())
            record = {**record, "decision_id": decision_id}
            self.decisions[decision_id] = deepcopy(record)
            return self.decisions[decision_id]

    def link_supersedes(self, new_id: str, old_id: str) -> None:
        with self._lock:
            if old_id in self.decisions:
                self.decisions[old_id]["superseded_by_id"] = new_id
            if new_id in self.decisions:
                self.decisions[new_id]["supersedes_id"] = old_id

    def snapshot_copy(self) -> MemoryStore:
        with self._lock:
            return deepcopy(self)
