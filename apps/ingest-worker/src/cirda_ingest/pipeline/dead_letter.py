"""Dead letter handling for permanently failed events."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import structlog

try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore[assignment]

from cirda_ingest.sinks.metrics_sink import MetricsSink

logger = structlog.get_logger(__name__)


class PermanentIngestError(Exception):
    """Non-retryable ingest failure (validation, schema, policy)."""


@dataclass(slots=True)
class DeadLetterRecord:
    raw: dict[str, Any]
    reason: str
    source: str
    failed_at: datetime
    detail: str | None = None


class DeadLetterQueue:
    """Store permanently failed events in Redis (with in-memory fallback)."""

    def __init__(
        self,
        redis_url: str | None,
        *,
        metrics: MetricsSink | None = None,
        key: str = "cirda:ingest:dlq",
    ) -> None:
        self._redis_url = redis_url
        self._metrics = metrics
        self._key = key
        self._redis: Any = None
        self._memory: list[DeadLetterRecord] = []

    async def connect(self) -> None:
        if not self._redis_url or aioredis is None:
            return
        try:
            client = aioredis.from_url(self._redis_url, decode_responses=True)
            await client.ping()
            self._redis = client
            logger.info("dlq_redis_connected", url=self._redis_url)
        except Exception as exc:
            logger.warning("dlq_redis_unavailable", error=str(exc))
            self._redis = None

    async def close(self) -> None:
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    async def send(self, record: DeadLetterRecord) -> None:
        payload = {
            "raw": record.raw,
            "reason": record.reason,
            "source": record.source,
            "failed_at": record.failed_at.isoformat(),
            "detail": record.detail,
        }
        if self._redis is not None:
            await self._redis.lpush(self._key, json.dumps(payload))
        else:
            self._memory.append(record)
        if self._metrics:
            self._metrics.record_dlq(record.reason)
        logger.warning(
            "ingest_dead_letter",
            reason=record.reason,
            source=record.source,
            detail=record.detail,
        )

    def memory_records(self) -> list[DeadLetterRecord]:
        return list(self._memory)

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
