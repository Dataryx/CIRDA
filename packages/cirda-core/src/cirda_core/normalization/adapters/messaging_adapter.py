"""Messaging evidence adapter."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_core.domain.enums import EvidenceChannel, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.normalization.normalizer import build_event


class MessagingAdapter:
    """Normalize message bus publish/consume records."""

    channel = EvidenceChannel.MESSAGING

    def can_handle(self, raw: dict[str, Any]) -> bool:
        return raw.get("source") == "messaging" or raw.get("channel") == self.channel.value

    def normalize(self, raw: dict[str, Any]) -> EvidenceEvent:
        observed_at = raw.get("observed_at") or raw.get("timestamp")
        if isinstance(observed_at, str):
            observed_at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if not isinstance(observed_at, datetime):
            raise ValueError("messaging adapter requires observed_at datetime")
        relation = Relation.PUBLISHES if raw.get("action") == "publish" else Relation.CONSUMES
        if "relation" in raw:
            relation = Relation(raw["relation"])
        return build_event(
            event_id=str(raw["event_id"]),
            source_id=str(raw["publisher_id"]),
            target_id=str(raw["topic_id"]),
            relation=relation,
            channel=self.channel,
            observed_at=observed_at,
            payload=raw.get("payload"),
        )
