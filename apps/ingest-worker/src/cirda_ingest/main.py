"""CIRDA ingest worker entrypoint."""

from __future__ import annotations

import asyncio
import signal
import time
from typing import Any

import structlog

from cirda_core.config.policy import PolicyConfig

from cirda_ingest.consumers.file_replay_consumer import FileReplayConsumer
from cirda_ingest.consumers.inmemory_consumer import InMemoryConsumer
from cirda_ingest.consumers.kafka_consumer import create_kafka_consumer
from cirda_ingest.consumers.otlp_receiver import OtlpReceiver
from cirda_ingest.health import HealthServer, HealthState
from cirda_ingest.logging_config import configure_logging
from cirda_ingest.pipeline.batcher import EventBatcher
from cirda_ingest.pipeline.checkpoint import CheckpointManager, OffsetToken
from cirda_ingest.pipeline.dead_letter import DeadLetterQueue, DeadLetterRecord, PermanentIngestError
from cirda_ingest.pipeline.stages import InboundMessage, IngestPipeline
from cirda_ingest.settings import Settings, get_settings
from cirda_ingest.sinks.metrics_sink import MetricsSink
from cirda_ingest.sinks.postgres_sink import PostgresSink

logger = structlog.get_logger(__name__)


class IngestWorker:
    """Orchestrates consumer, batching, pipeline, checkpointing, and health."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.metrics = MetricsSink()
        self.health = HealthState()
        self.sink = PostgresSink(
            settings.effective_database_url,
            memory_mode=settings.use_memory_store,
        )
        policy = PolicyConfig(
            theta_confirmed=settings.theta_c,
            theta_possible=settings.theta_p,
            c_min=settings.c_min,
            confirmed_requires_direct_evidence=settings.confirmed_requires_direct_evidence,
            min_trace_observations_for_confirmed=settings.min_trace_observations_for_confirmed,
        )
        self.pipeline = IngestPipeline(self.sink, policy=policy, metrics=self.metrics)
        self.dlq = DeadLetterQueue(settings.redis_url, metrics=self.metrics)
        self.checkpoint = CheckpointManager(metrics=self.metrics)
        self._inmemory: InMemoryConsumer | None = None
        self._kafka_worker: Any = None
        self._file_consumer: FileReplayConsumer | None = None
        self._otlp: OtlpReceiver | None = None
        self._batcher: EventBatcher | None = None
        self._health_server: HealthServer | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        configure_logging(self.settings)
        await self.sink.initialize()
        await self.dlq.connect()

        self._batcher = EventBatcher(
            self._handle_batch,
            max_events=self.settings.batch_max_events,
            max_wait_seconds=self.settings.batch_max_wait_seconds,
        )

        mode = self.settings.event_bus
        if mode == "kafka":
            worker, fallback = await create_kafka_consumer(self.settings)
            if worker is None:
                logger.warning("kafka_fallback_to_inmemory", reason=fallback)
                mode = "inmemory"
                self.health.kafka_connected = False
            else:
                self._kafka_worker = worker
                self.checkpoint = CheckpointManager(worker.committer, metrics=self.metrics)
                await worker.start(self._enqueue)
                self.health.kafka_connected = True

        if mode == "inmemory":
            self._inmemory = InMemoryConsumer()
            await self._inmemory.start(self._enqueue)
            self.health.consumer_mode = "inmemory"
        elif mode == "file":
            self._file_consumer = FileReplayConsumer(
                self.settings.file_replay_path,
                loop=self.settings.file_replay_loop,
            )
            await self._file_consumer.start(self._enqueue)
            self.health.consumer_mode = "file"
        elif mode == "otlp":
            self._otlp = OtlpReceiver(self.settings.otlp_listen_host, self.settings.otlp_listen_port)
            await self._otlp.start(self._enqueue)
            self.health.consumer_mode = "otlp"
        elif mode == "kafka" and self._kafka_worker is not None:
            self.health.consumer_mode = "kafka"
        else:
            self.health.consumer_mode = mode

        dev_publish = self._inmemory.publish if self._inmemory is not None else None
        self._health_server = HealthServer(
            self.settings.host,
            self.settings.port,
            health=self.health,
            metrics_enabled=self.settings.metrics_enabled,
            on_dev_publish=dev_publish,
        )
        await self._health_server.start()
        self.health.ready = True
        logger.info(
            "ingest_worker_started",
            mode=self.health.consumer_mode,
            host=self.settings.host,
            port=self.settings.port,
        )

    async def stop(self) -> None:
        self.health.ready = False
        if self._batcher is not None:
            await self._batcher.close()
        if self._inmemory is not None:
            await self._inmemory.stop()
        if self._kafka_worker is not None:
            await self._kafka_worker.stop()
        if self._file_consumer is not None:
            await self._file_consumer.stop()
        if self._otlp is not None:
            await self._otlp.stop()
        if self._health_server is not None:
            await self._health_server.stop()
        await self.dlq.close()
        await self.sink.close()
        self._stop_event.set()

    async def _enqueue(self, message: InboundMessage) -> None:
        self.metrics.record_received(message.source)
        token = OffsetToken(
            message_id=message.message_id,
            topic=message.topic,
            partition=message.partition,
            offset=message.offset,
        )
        self.checkpoint.register(token)
        assert self._batcher is not None
        await self._batcher.add(message)

    async def _handle_batch(self, messages: list[InboundMessage]) -> None:
        started = time.perf_counter()
        try:
            result = await self.pipeline.process_batch(messages)
        except Exception as exc:
            self.health.last_error = str(exc)
            logger.exception("batch_processing_failed")
            raise

        for item in result.permanent_failures:
            await self.dlq.send(
                DeadLetterRecord(
                    raw=item.raw,
                    reason="permanent",
                    source=item.message.source,
                    failed_at=DeadLetterQueue.now(),
                    detail=str(item.permanent_error),
                )
            )

        durable_ids = list(result.persist.durable_message_ids)
        durable_ids.extend(item.message.message_id for item in result.permanent_failures)
        self.checkpoint.mark_durable(durable_ids)
        await self.checkpoint.commit_durable()

        self.health.events_processed += len(result.persist.created_event_ids)
        self.health.last_error = None
        self.metrics.record_batch(time.perf_counter() - started)

    async def run_forever(self) -> None:
        await self.start()
        await self._stop_event.wait()


async def _async_main() -> None:
    settings = get_settings()
    worker = IngestWorker(settings)
    loop = asyncio.get_running_loop()

    async def _shutdown() -> None:
        logger.info("shutdown_signal_received")
        await worker.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))
        except NotImplementedError:
            pass

    try:
        await worker.run_forever()
    finally:
        await worker.stop()


def main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
