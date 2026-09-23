"""In-memory asyncio queue consumer for dev-lite (CIRDA_EVENT_BUS=inmemory)."""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

from cirda_ingest.pipeline.stages import InboundMessage

logger = structlog.get_logger(__name__)

MessageHandler = Callable[[InboundMessage], Awaitable[None]]


class InMemoryConsumer:
    """Publish/subscribe over an asyncio queue — no external broker required."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self._handler: MessageHandler | None = None
        self._task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self, handler: MessageHandler) -> None:
        self._handler = handler
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("inmemory_consumer_started")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def publish(self, raw: dict[str, Any], *, idempotency_key: str | None = None) -> None:
        message = InboundMessage(
            raw=raw,
            message_id=str(uuid.uuid4()),
            source="inmemory",
            idempotency_key=idempotency_key,
        )
        await self._queue.put(message)

    async def _run(self) -> None:
        assert self._handler is not None
        while self._running:
            try:
                message = await asyncio.wait_for(self._queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            await self._handler(message)
            self._queue.task_done()
