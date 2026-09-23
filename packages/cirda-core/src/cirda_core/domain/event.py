"""Evidence event domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cirda_core.domain.enums import EntityType, EvidenceChannel, Relation
from cirda_core.domain.errors import NaiveDatetimeError


def _require_aware(dt: datetime, field_name: str) -> None:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveDatetimeError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class EvidenceEvent:
    """Raw observation of an inter-entity interaction."""

    event_id: str
    source_id: str
    target_id: str
    relation: Relation
    channel: EvidenceChannel
    observed_at: datetime
    source_type: EntityType | None = None
    target_type: EntityType | None = None
    payload_hash: str | None = None

    def __post_init__(self) -> None:
        _require_aware(self.observed_at, "observed_at")
        if not self.event_id:
            raise ValueError("event_id must be non-empty")
        if not self.source_id or not self.target_id:
            raise ValueError("source_id and target_id must be non-empty")
