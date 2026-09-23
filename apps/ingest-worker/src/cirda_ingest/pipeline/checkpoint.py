"""Checkpoint manager — commit consumer offsets only after durable writes."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Protocol

import structlog

from cirda_ingest.sinks.metrics_sink import MetricsSink

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class OffsetToken:
    """Opaque consumer offset reference."""

    message_id: str
    topic: str | None = None
    partition: int | None = None
    offset: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class OffsetCommitter(Protocol):
    """Consumer-specific offset commit hook."""

    async def commit(self, tokens: list[OffsetToken]) -> None:
        ...


class InMemoryCommitter:
    """Test/dev committer that records committed message ids."""

    def __init__(self) -> None:
        self.committed: list[str] = []

    async def commit(self, tokens: list[OffsetToken]) -> None:
        self.committed.extend(token.message_id for token in tokens)


class CheckpointManager:
    """
    Tracks pending messages and commits offsets only after durable persistence.

    Ordering guarantee: commit happens strictly after sink.persist_batch succeeds.
    """

    def __init__(
        self,
        committer: OffsetCommitter | None = None,
        *,
        metrics: MetricsSink | None = None,
    ) -> None:
        self._committer = committer or InMemoryCommitter()
        self._metrics = metrics
        self._lock = asyncio.Lock()
        self._pending: dict[str, OffsetToken] = {}
        self._durable: set[str] = set()

    def register(self, token: OffsetToken) -> None:
        self._pending[token.message_id] = token

    def mark_durable(self, message_ids: list[str]) -> None:
        for mid in message_ids:
            if mid in self._pending:
                self._durable.add(mid)

    async def commit_durable(self) -> int:
        """Commit all offsets whose messages have been durably written."""
        async with self._lock:
            ready = [self._pending[mid] for mid in sorted(self._durable) if mid in self._pending]
            if not ready:
                return 0
            await self._committer.commit(ready)
            for token in ready:
                self._durable.discard(token.message_id)
                self._pending.pop(token.message_id, None)
            if self._metrics:
                self._metrics.record_checkpoint()
            logger.debug("checkpoint_committed", count=len(ready))
            return len(ready)

    @property
    def pending_count(self) -> int:
        return len(self._pending)

    @property
    def durable_pending_commit_count(self) -> int:
        return len(self._durable)
