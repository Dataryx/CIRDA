"""Prometheus metrics for ingest worker."""

from __future__ import annotations

from prometheus_client import Counter, Histogram, generate_latest

EVENTS_RECEIVED = Counter(
    "cirda_ingest_worker_events_received_total",
    "Raw events received from consumers",
    ["source"],
)
EVENTS_PERSISTED = Counter(
    "cirda_ingest_worker_events_persisted_total",
    "Evidence events durably persisted",
    ["created"],
)
EVENTS_DEDUPED = Counter("cirda_ingest_worker_events_deduped_total", "Duplicate event_id skips")
EDGES_UPDATED = Counter("cirda_ingest_worker_edges_updated_total", "Dependency edges upserted")
BATCHES = Counter("cirda_ingest_worker_batches_total", "Processed ingest batches")
BATCH_LATENCY = Histogram(
    "cirda_ingest_worker_batch_duration_seconds",
    "Batch processing latency",
)
DLQ_SENT = Counter(
    "cirda_ingest_worker_dlq_total",
    "Events sent to dead letter queue",
    ["reason"],
)
CHECKPOINT_COMMITS = Counter("cirda_ingest_worker_checkpoint_commits_total", "Offset checkpoint commits")


def metrics_payload() -> bytes:
    return generate_latest()


class MetricsSink:
    """Record pipeline outcomes to Prometheus."""

    def record_received(self, source: str, count: int = 1) -> None:
        EVENTS_RECEIVED.labels(source=source).inc(count)

    def record_persist(self, *, created: int, deduped: int, edges: int) -> None:
        if created:
            EVENTS_PERSISTED.labels(created="true").inc(created)
        if deduped:
            EVENTS_DEDUPED.inc(deduped)
        if edges:
            EDGES_UPDATED.inc(edges)

    def record_batch(self, duration_seconds: float) -> None:
        BATCHES.inc()
        BATCH_LATENCY.observe(duration_seconds)

    def record_dlq(self, reason: str, count: int = 1) -> None:
        DLQ_SENT.labels(reason=reason).inc(count)

    def record_checkpoint(self) -> None:
        CHECKPOINT_COMMITS.inc()
