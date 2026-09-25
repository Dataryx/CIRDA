"""Kafka consumer using aiokafka with graceful fallback when brokers are unavailable."""

from __future__ import annotations

import asyncio
import json
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

from cirda_ingest.pipeline.checkpoint import OffsetCommitter, OffsetToken
from cirda_ingest.pipeline.stages import InboundMessage
from cirda_ingest.settings import Settings

logger = structlog.get_logger(__name__)

MessageHandler = Callable[[InboundMessage], Awaitable[None]]


class KafkaOffsetCommitter(OffsetCommitter):
    """Commits highest contiguous processed offsets per partition."""

    def __init__(self, consumer: Any) -> None:
        self._consumer = consumer
        self._highwater: dict[tuple[str, int], int] = {}

    async def commit(self, tokens: list[OffsetToken]) -> None:
        from aiokafka.structs import TopicPartition

        by_tp: dict[tuple[str, int], int] = {}
        for token in tokens:
            if token.topic is None or token.partition is None or token.offset is None:
                continue
            key = (token.topic, token.partition)
            by_tp[key] = max(by_tp.get(key, -1), token.offset + 1)

        offsets = {
            TopicPartition(topic, partition): offset
            for (topic, partition), offset in by_tp.items()
        }
        if offsets:
            await self._consumer.commit(offsets)


class KafkaConsumerWorker:
    """Consume raw evidence from Kafka; falls back when brokers are unreachable."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._consumer: Any = None
        self._committer: KafkaOffsetCommitter | None = None
        self._handler: MessageHandler | None = None
        self._task: asyncio.Task[None] | None = None
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def committer(self) -> KafkaOffsetCommitter | None:
        return self._committer

    async def try_connect(self) -> bool:
        try:
            from aiokafka import AIOKafkaConsumer
        except ImportError as exc:
            logger.error("aiokafka_not_installed", error=str(exc))
            return False

        consumer = AIOKafkaConsumer(
            self._settings.kafka_topic,
            bootstrap_servers=self._settings.kafka_bootstrap_servers,
            group_id=self._settings.kafka_group_id,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            value_deserializer=lambda b: json.loads(b.decode("utf-8").strip()),
        )
        try:
            await asyncio.wait_for(consumer.start(), timeout=5.0)
        except Exception as exc:
            logger.warning(
                "kafka_connect_failed",
                brokers=self._settings.kafka_bootstrap_servers,
                error=str(exc),
            )
            try:
                await consumer.stop()
            except Exception:
                pass
            return False

        self._consumer = consumer
        self._committer = KafkaOffsetCommitter(consumer)
        self._connected = True
        logger.info(
            "kafka_consumer_connected",
            topic=self._settings.kafka_topic,
            group=self._settings.kafka_group_id,
        )
        return True

    async def start(self, handler: MessageHandler) -> None:
        if self._consumer is None:
            raise RuntimeError("Kafka consumer not connected")
        self._handler = handler
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            self._committer = None
            self._connected = False

    async def _run(self) -> None:
        assert self._consumer is not None and self._handler is not None
        wait_ms = max(50, int(self._settings.batch_max_wait_seconds * 1000))
        try:
            while True:
                batches = await self._consumer.getmany(
                    timeout_ms=wait_ms,
                    max_records=self._settings.batch_max_events,
                )
                if not batches:
                    # Idle: ask handler to flush any partial micro-batch.
                    await self._handler(
                        InboundMessage(raw={"__flush__": True}, message_id="__flush__", source="kafka")
                    )
                    continue
                for _tp, records in batches.items():
                    for record in records:
                        raw = record.value
                        if not isinstance(raw, dict):
                            logger.warning("kafka_invalid_payload", offset=record.offset)
                            continue
                        message = InboundMessage(
                            raw=raw,
                            message_id=f"{record.topic}:{record.partition}:{record.offset}",
                            source="kafka",
                            idempotency_key=raw.get("idempotency_key"),
                            topic=record.topic,
                            partition=record.partition,
                            offset=record.offset,
                        )
                        await self._handler(message)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("kafka_consume_loop_failed")
            raise


async def create_kafka_consumer(settings: Settings) -> tuple[KafkaConsumerWorker | None, str | None]:
    """
    Attempt Kafka connection; return (worker, fallback_reason).

    When brokers are unavailable and auto_fallback is enabled, returns (None, reason).
    """
    worker = KafkaConsumerWorker(settings)
    if await worker.try_connect():
        return worker, None
    if settings.kafka_auto_fallback:
        return None, "kafka_unavailable"
    raise RuntimeError(
        f"Unable to connect to Kafka at {settings.kafka_bootstrap_servers}"
    )
