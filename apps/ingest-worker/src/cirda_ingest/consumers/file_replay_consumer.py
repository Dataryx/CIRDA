"""Replay JSONL evidence files for backfill and local testing."""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import structlog

from cirda_ingest.pipeline.stages import InboundMessage

logger = structlog.get_logger(__name__)

MessageHandler = Callable[[InboundMessage], Awaitable[None]]


class FileReplayConsumer:
    """Read newline-delimited JSON evidence records and push into the pipeline."""

    def __init__(self, path: str, *, loop: bool = False, poll_interval: float = 1.0) -> None:
        self._path = Path(path)
        self._loop = loop
        self._poll_interval = poll_interval
        self._handler: MessageHandler | None = None
        self._task: asyncio.Task[None] | None = None
        self._running = False
        self._line_index = 0

    async def start(self, handler: MessageHandler) -> None:
        self._handler = handler
        self._running = True
        self._task = asyncio.create_task(self._run())
        logger.info("file_replay_started", path=str(self._path), loop=self._loop)

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _run(self) -> None:
        assert self._handler is not None
        while self._running:
            if not self._path.exists():
                logger.warning("file_replay_missing", path=str(self._path))
                await asyncio.sleep(self._poll_interval)
                continue

            with self._path.open("r", encoding="utf-8") as fh:
                for idx, line in enumerate(fh):
                    if not self._running:
                        return
                    if idx < self._line_index:
                        continue
                    line = line.strip()
                    if not line:
                        self._line_index = idx + 1
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError as exc:
                        logger.warning("file_replay_invalid_json", line=idx, error=str(exc))
                        self._line_index = idx + 1
                        continue
                    if not isinstance(raw, dict):
                        self._line_index = idx + 1
                        continue
                    message = InboundMessage(
                        raw=raw,
                        message_id=f"file:{self._path.name}:{idx}",
                        source="file",
                        idempotency_key=raw.get("idempotency_key"),
                    )
                    await self._handler(message)
                    self._line_index = idx + 1

            if not self._loop:
                logger.info("file_replay_complete", path=str(self._path))
                return
            await asyncio.sleep(self._poll_interval)
