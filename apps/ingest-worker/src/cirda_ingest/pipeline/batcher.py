"""Micro-batching: flush at 200ms or 500 events (whichever comes first)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from cirda_ingest.pipeline.stages import InboundMessage

logger = structlog.get_logger(__name__)

BatchHandler = Callable[[list["InboundMessage"]], Awaitable[None]]


class EventBatcher:
    """Accumulates inbound messages and flushes by size or time window."""

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
        self._lock = asyncio.Lock()
        self._flush_task: asyncio.Task[None] | None = None
        self._closed = False

    async def add(self, message: InboundMessage) -> None:
        flush_now = False
        async with self._lock:
            if self._closed:
                return
            self._buffer.append(message)
            if len(self._buffer) >= self._max_events:
                flush_now = True
            elif self._flush_task is None:
                self._flush_task = asyncio.create_task(self._delayed_flush())

        if flush_now:
            await self.flush()

    async def _delayed_flush(self) -> None:
        try:
            await asyncio.sleep(self._max_wait_seconds)
            await self.flush()
        except asyncio.CancelledError:
            pass

    async def flush(self) -> None:
        batch: list[InboundMessage] = []
        async with self._lock:
            if self._flush_task is not None:
                self._flush_task.cancel()
                self._flush_task = None
            if not self._buffer:
                return
            batch = self._buffer
            self._buffer = []

        logger.debug("batch_flush", size=len(batch))
        await self._handler(batch)

    async def close(self) -> None:
        async with self._lock:
            self._closed = True
            if self._flush_task is not None:
                self._flush_task.cancel()
                self._flush_task = None
        await self.flush()
