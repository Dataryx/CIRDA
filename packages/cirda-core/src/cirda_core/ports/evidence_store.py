"""Evidence store protocol."""

from __future__ import annotations

from typing import Protocol

from cirda_core.domain.enums import EvidenceChannel
from cirda_core.domain.event import EvidenceEvent


class EvidenceStore(Protocol):
    """Persistence port for raw evidence events."""

    def add_event(self, event: EvidenceEvent) -> None:
        ...

    def get_events(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        channel: EvidenceChannel | None = None,
    ) -> list[EvidenceEvent]:
        ...

    def count_observations(
        self,
        source_id: str,
        target_id: str,
        channel: EvidenceChannel,
    ) -> int:
        ...
