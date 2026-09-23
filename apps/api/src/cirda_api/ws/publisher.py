"""Publish domain events to WebSocket subscribers."""

from __future__ import annotations

from typing import Any

from cirda_core.domain.event import EvidenceEvent

from cirda_api.ws import topics
from cirda_api.ws.manager import ConnectionManager


class EventPublisher:
    def __init__(self, manager: ConnectionManager) -> None:
        self.manager = manager

    async def publish_evidence(self, event: EvidenceEvent) -> None:
        await self.manager.broadcast(
            topics.EVIDENCE,
            {
                "event_id": event.event_id,
                "source_id": event.source_id,
                "target_id": event.target_id,
                "channel": event.channel.value,
                "observed_at": event.observed_at.isoformat(),
            },
        )

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        await self.manager.broadcast(topic, payload)
