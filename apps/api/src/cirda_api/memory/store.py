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
    entity_tenants: dict[str, str] = field(default_factory=dict)
    entity_metadata: dict[str, dict[str, Any]] = field(default_factory=dict)
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
    # entity_id -> channel values restored by probe apply (suppression lift)
    probe_restorations: dict[str, set[str]] = field(default_factory=dict)
    calibration_profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    benchmark_runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    benchmark_results: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    principals: dict[str, dict[str, Any]] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def _entity_key(self, entity_id: str) -> str:
        from cirda_api.security.tenant import tenant_scoped_key

        return tenant_scoped_key(entity_id)

    def _resource_key(self, resource_id: str) -> str:
        from cirda_api.security.tenant import tenant_scoped_key

        return tenant_scoped_key(resource_id)

    def _current_tenant(self) -> str:
        from cirda_api.security.tenant import get_current_tenant_id

        return get_current_tenant_id()

    def upsert_entity_record(
        self,
        *,
        entity_id: str,
        entity_type: str,
        name: str,
        criticality: str = "unknown",
        metadata: dict[str, Any] | None = None,
        aliases: list[str] | None = None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        ts = now or _utcnow()
        key = self._entity_key(entity_id)
        with self._lock:
            existing = self.entities.get(key)
            alias_set = frozenset(aliases or [])
            if aliases is None and existing is not None:
                alias_set = existing.aliases
            entity = Entity(
                entity_id=entity_id,
                entity_type=EntityType(entity_type),
                name=name,
                criticality=Criticality(criticality),
                aliases=alias_set,
            )
            self.entities[key] = entity
            tenant = self._current_tenant()
            self.entity_tenants[key] = tenant
            if metadata is not None or key not in self.entity_metadata:
                self.entity_metadata[key] = dict(metadata or {})
            if aliases is not None:
                self.aliases[key] = [(a, "api") for a in aliases]
            record = {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "name": name,
                "criticality": criticality,
                "metadata": dict(self.entity_metadata.get(key, {})),
                "aliases": [a[0] for a in self.aliases.get(key, [])],
                "tenant_id": tenant,
                "created_at": ts if existing is None else getattr(existing, "_created_at", ts),
                "updated_at": ts,
            }
            return record

    def add_alias(self, entity_id: str, alias: str, source: str | None = None) -> None:
        key = self._entity_key(entity_id)
        with self._lock:
            existing_aliases = self.aliases.get(key, [])
            if any(a == alias for a, _ in existing_aliases):
                return
            self.aliases.setdefault(key, []).append((alias, source))
            entity = self.entities.get(key)
            if entity is not None:
                self.entities[key] = Entity(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    name=entity.name,
                    criticality=entity.criticality,
                    aliases=frozenset({*entity.aliases, alias}),
                    metadata=entity.metadata,
                )

    def add_evidence(self, event: EvidenceEvent, idempotency_key: str | None = None) -> tuple[EvidenceEvent, bool]:
        with self._lock:
            event_key = self._resource_key(event.event_id)
            if idempotency_key:
                idem_key = self._resource_key(idempotency_key)
                if idem_key in self.idempotency_index:
                    existing_id = self.idempotency_index[idem_key]
                    return self.evidence_events[existing_id], False
            if event_key in self.evidence_events:
                return self.evidence_events[event_key], False
            self.evidence_events[event_key] = event
            if idempotency_key:
                self.idempotency_index[self._resource_key(idempotency_key)] = event_key
            return event, True

    def upsert_edge_record(self, edge: DependencyEdge, *, valid_from: datetime, valid_to: datetime | None = None) -> dict[str, Any]:
        edge_id = edge.edge_id or f"{edge.source_id}->{edge.target_id}:{edge.relation.value}"
        key = self._resource_key(edge_id)
        now = _utcnow()
        tenant = self._current_tenant()
        with self._lock:
            existing = self.edges.get(key)
            necessity = edge.necessity.value
            # Preserve operator annotations when fusion still reports unknown.
            if (
                existing
                and existing.get("necessity", "unknown") != Necessity.UNKNOWN.value
                and edge.necessity == Necessity.UNKNOWN
            ):
                necessity = existing["necessity"]
            record = {
                "edge_id": edge_id,
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "relation": edge.relation.value,
                "layer": edge.layer.value,
                "confidence": edge.confidence,
                "necessity": necessity,
                "evidence_count": edge.evidence_count,
                "tenant_id": tenant,
                "last_observed_at": datetime.fromtimestamp(edge.last_observed_epoch, tz=timezone.utc)
                if edge.last_observed_epoch
                else now,
                "valid_from": valid_from if existing is None else existing.get("valid_from", valid_from),
                "valid_to": valid_to if existing is None else existing.get("valid_to", valid_to),
                "created_at": existing["created_at"] if existing else now,
                "updated_at": now,
            }
            self.edges[key] = record
            self.edge_channel_evidence.setdefault(key, {})
            return record

    def update_edge_necessity(self, edge_id: str, necessity: str) -> dict[str, Any] | None:
        key = self._resource_key(edge_id)
        with self._lock:
            row = self.edges.get(key)
            if not row:
                return None
            row = {**row, "necessity": necessity, "updated_at": _utcnow()}
            self.edges[key] = row
            return deepcopy(row)

    def increment_channel_evidence(self, edge_id: str, channel: str, observed_at: datetime) -> None:
        key = self._resource_key(edge_id)
        with self._lock:
            ch_map = self.edge_channel_evidence.setdefault(key, {})
            entry = ch_map.get(channel, {"observation_count": 0, "last_observed_at": observed_at})
            entry["observation_count"] += 1
            entry["last_observed_at"] = observed_at
            ch_map[channel] = entry

    def create_decision(self, record: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            decision_id = record.get("decision_id") or str(uuid.uuid4())
            key = self._resource_key(decision_id)
            record = {**record, "decision_id": decision_id, "tenant_id": self._current_tenant()}
            executions = record.get("runbook_executions")
            if executions is None:
                executions = []
                for action in (record.get("rationale") or {}).get("suggested_runbook") or []:
                    executions.append(
                        {
                            "execution_id": str(uuid.uuid4()),
                            "decision_id": decision_id,
                            "stage": action["stage"],
                            "status": "pending",
                            "started_at": None,
                            "completed_at": None,
                            "notes": None,
                            "description": action.get("description"),
                        }
                    )
            record = {**record, "runbook_executions": executions}
            self.decisions[key] = deepcopy(record)
            self.runbook_executions[key] = deepcopy(executions)
            return self.decisions[key]

    def list_runbook_executions(self, decision_id: str) -> list[dict[str, Any]]:
        key = self._resource_key(decision_id)
        with self._lock:
            return deepcopy(self.runbook_executions.get(key, []))

    def update_runbook_execution(
        self,
        decision_id: str,
        execution_id: str,
        *,
        status: str,
        notes: str | None = None,
    ) -> dict[str, Any] | None:
        key = self._resource_key(decision_id)
        with self._lock:
            rows = self.runbook_executions.get(key)
            if not rows:
                return None
            now = _utcnow()
            for i, row in enumerate(rows):
                if row["execution_id"] != execution_id:
                    continue
                updated = {**row, "status": status}
                if notes is not None:
                    updated["notes"] = notes
                if status == "in_progress" and not updated.get("started_at"):
                    updated["started_at"] = now
                if status == "completed":
                    if not updated.get("started_at"):
                        updated["started_at"] = now
                    updated["completed_at"] = now
                rows[i] = updated
                self.runbook_executions[key] = rows
                if key in self.decisions:
                    self.decisions[key]["runbook_executions"] = deepcopy(rows)
                return deepcopy(updated)
            return None

    def link_supersedes(self, new_id: str, old_id: str) -> None:
        with self._lock:
            old_key = self._resource_key(old_id)
            new_key = self._resource_key(new_id)
            if old_key in self.decisions:
                self.decisions[old_key]["superseded_by_id"] = new_id
            if new_key in self.decisions:
                self.decisions[new_key]["supersedes_id"] = old_id

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        key = self._resource_key(decision_id)
        with self._lock:
            row = self.decisions.get(key)
            return deepcopy(row) if row else None

    def iter_tenant_edges(self) -> list[dict[str, Any]]:
        prefix = f"{self._current_tenant()}::"
        with self._lock:
            return [deepcopy(v) for k, v in self.edges.items() if k.startswith(prefix)]

    def get_edge(self, edge_id: str) -> dict[str, Any] | None:
        key = self._resource_key(edge_id)
        with self._lock:
            row = self.edges.get(key)
            return deepcopy(row) if row else None

    def iter_tenant_evidence(self) -> list[EvidenceEvent]:
        prefix = f"{self._current_tenant()}::"
        with self._lock:
            return [v for k, v in self.evidence_events.items() if k.startswith(prefix)]

    def get_evidence(self, event_id: str) -> EvidenceEvent | None:
        key = self._resource_key(event_id)
        with self._lock:
            return self.evidence_events.get(key)

    def iter_tenant_decisions(self) -> list[dict[str, Any]]:
        prefix = f"{self._current_tenant()}::"
        with self._lock:
            return [deepcopy(v) for k, v in self.decisions.items() if k.startswith(prefix)]

    def iter_tenant_coverage_snapshots(self) -> list[dict[str, Any]]:
        tenant = self._current_tenant()
        with self._lock:
            return [
                deepcopy(s)
                for s in self.coverage_snapshots
                if s.get("tenant_id", "default") == tenant
            ]

    def append_coverage_snapshot(self, record: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            stamped = {**record, "tenant_id": self._current_tenant()}
            self.coverage_snapshots.append(stamped)
            return deepcopy(stamped)

    def get_channel_health(self, channel: str) -> dict[str, Any] | None:
        key = self._resource_key(channel)
        with self._lock:
            row = self.channel_health.get(key)
            return deepcopy(row) if row else None

    def set_channel_health(self, channel: str, payload: dict[str, Any]) -> None:
        key = self._resource_key(channel)
        with self._lock:
            self.channel_health[key] = {**payload, "tenant_id": self._current_tenant()}

    def iter_tenant_channel_health(self) -> list[dict[str, Any]]:
        prefix = f"{self._current_tenant()}::"
        with self._lock:
            return [deepcopy(v) for k, v in self.channel_health.items() if k.startswith(prefix)]

    def get_probe_restorations(self, entity_id: str) -> set[str]:
        key = self._resource_key(entity_id)
        with self._lock:
            return set(self.probe_restorations.get(key, set()))

    def set_probe_restorations(self, entity_id: str, channels: set[str]) -> None:
        key = self._resource_key(entity_id)
        with self._lock:
            self.probe_restorations[key] = set(channels)

    def snapshot_copy(self) -> MemoryStore:
        with self._lock:
            return deepcopy(self)
