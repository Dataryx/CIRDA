"""Static declared evidence adapter."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_core.domain.enums import EvidenceChannel, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.normalization.normalizer import build_event


class StaticAdapter:
    """Normalize statically declared dependency manifests."""

    channel = EvidenceChannel.STATIC_DECLARED

    def can_handle(self, raw: dict[str, Any]) -> bool:
        return raw.get("source") == "static" or raw.get("channel") == self.channel.value

    def normalize(self, raw: dict[str, Any]) -> EvidenceEvent:
        observed_at = raw.get("observed_at") or raw.get("declared_at")
        if isinstance(observed_at, str):
            observed_at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if not isinstance(observed_at, datetime):
            raise ValueError("static adapter requires observed_at datetime")
        return build_event(
            event_id=str(raw["event_id"]),
            source_id=str(raw["source_id"]),
            target_id=str(raw["target_id"]),
            relation=Relation(raw.get("relation", "calls")),
            channel=self.channel,
            observed_at=observed_at,
            payload=raw.get("payload"),
        )
