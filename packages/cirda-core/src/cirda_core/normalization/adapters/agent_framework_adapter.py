"""Agent framework evidence adapter."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cirda_core.domain.enums import EvidenceChannel, Relation
from cirda_core.domain.event import EvidenceEvent
from cirda_core.normalization.normalizer import build_event


class AgentFrameworkAdapter:
    """Normalize agent framework delegation/tool-call records."""

    channel = EvidenceChannel.AGENT_FRAMEWORK

    def can_handle(self, raw: dict[str, Any]) -> bool:
        return raw.get("source") == "agent_framework" or raw.get("channel") == self.channel.value

    def normalize(self, raw: dict[str, Any]) -> EvidenceEvent:
        observed_at = raw.get("observed_at") or raw.get("timestamp")
        if isinstance(observed_at, str):
            observed_at = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if not isinstance(observed_at, datetime):
            raise ValueError("agent_framework adapter requires observed_at datetime")
        action = raw.get("action", "delegate")
        relation_map = {
            "delegate": Relation.DELEGATES,
            "call": Relation.CALLS,
            "uses_model": Relation.USES_MODEL,
        }
        relation = relation_map.get(str(action), Relation.DELEGATES)
        if "relation" in raw:
            relation = Relation(raw["relation"])
        return build_event(
            event_id=str(raw["event_id"]),
            source_id=str(raw["agent_id"]),
            target_id=str(raw["target_id"]),
            relation=relation,
            channel=self.channel,
            observed_at=observed_at,
            payload=raw.get("payload"),
        )
