"""Evidence normalization pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Protocol

from cirda_core.domain.enums import EntityType, EvidenceChannel, Relation
from cirda_core.domain.errors import NaiveDatetimeError
from cirda_core.domain.event import EvidenceEvent
from cirda_core.normalization.redaction import redact_value


class EvidenceAdapter(Protocol):
    """Adapter for a specific evidence source format."""

    channel: EvidenceChannel

    def can_handle(self, raw: dict[str, Any]) -> bool:
        ...

    def normalize(self, raw: dict[str, Any]) -> EvidenceEvent:
        ...


def ensure_aware(dt: datetime) -> datetime:
    """Convert naive datetimes to UTC or reject."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveDatetimeError("datetime must be timezone-aware")
    return dt.astimezone(timezone.utc)


def build_event(
    *,
    event_id: str,
    source_id: str,
    target_id: str,
    relation: Relation,
    channel: EvidenceChannel,
    observed_at: datetime,
    source_type: EntityType | None = None,
    target_type: EntityType | None = None,
    payload: dict[str, Any] | None = None,
) -> EvidenceEvent:
    """Build a normalized evidence event with redacted payload hash."""
    aware_at = ensure_aware(observed_at)
    payload_hash = None
    if payload is not None:
        redacted = redact_value(payload)
        payload_hash = str(hash(frozenset(redacted.items()) if isinstance(redacted, dict) else redacted))
    return EvidenceEvent(
        event_id=event_id,
        source_id=source_id,
        target_id=target_id,
        relation=relation,
        channel=channel,
        observed_at=aware_at,
        source_type=source_type,
        target_type=target_type,
        payload_hash=payload_hash,
    )


class Normalizer:
    """Route raw evidence through registered adapters."""

    def __init__(self, adapters: list[EvidenceAdapter] | None = None) -> None:
        self._adapters: list[EvidenceAdapter] = adapters or []

    def register(self, adapter: EvidenceAdapter) -> None:
        self._adapters.append(adapter)

    def normalize(self, raw: dict[str, Any]) -> EvidenceEvent:
        for adapter in self._adapters:
            if adapter.can_handle(raw):
                return adapter.normalize(raw)
        raise ValueError("No adapter found for raw evidence")
