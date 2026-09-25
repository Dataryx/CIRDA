"""Micro-batching: flush at max_wait or max_events (same-task safe)."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from cirda_ingest.pipeline.stages import InboundMessage

logger = structlog.get_logger(__name__)

BatchHandler = Callable[[list["InboundMessage"]], Awaitable[None]]


class EventBatcher:
    """Accumulates inbound messages and flushes by size or time window.

    Designed for single-task use (e.g. Kafka consume loop): never schedules
    background tasks that touch the consumer/committer from another task.
    """

    def __init__(
        self,
        handler: BatchHandler,
        *,
        max_events: int = 500,
        max_wait_seconds: float = 0.2,
    ) -> None:
        self._handler = handler
        self._max_events = max_events
        self._max_wait_seconds = max_wait_seconds
        self._buffer: list[InboundMessage] = []
        self._window_start: float | None = None
        self._closed = False

    async def add(self, message: InboundMessage) -> None:
        if self._closed:
            return
        if self._window_start is None:
            self._window_start = time.monotonic()
        self._buffer.append(message)
        if len(self._buffer) >= self._max_events:
            await self.flush()

    async def flush_if_due(self) -> None:
        """Flush when the time window has elapsed (call from the consumer loop)."""
        if self._closed or not self._buffer or self._window_start is None:
            return
        if time.monotonic() - self._window_start >= self._max_wait_seconds:
            await self.flush()

    async def flush(self) -> None:
        if not self._buffer:
            self._window_start = None
            return
        batch = self._buffer
        self._buffer = []
        self._window_start = None
        logger.debug("batch_flush", size=len(batch))
        try:
            await self._handler(batch)
        except Exception:
            logger.exception("batch_flush_failed")
            raise

    async def close(self) -> None:
        self._closed = True
        await self.flush()
