"""Event bus protocol."""

from __future__ import annotations

from typing import Callable, Protocol

from cirda_core.domain.event import EvidenceEvent


EventHandler = Callable[[EvidenceEvent], None]


class EventBus(Protocol):
    """Publish/subscribe port for evidence events."""

    def publish(self, event: EvidenceEvent) -> None:
        ...

    def subscribe(self, handler: EventHandler) -> None:
        ...

    def unsubscribe(self, handler: EventHandler) -> None:
        ...
