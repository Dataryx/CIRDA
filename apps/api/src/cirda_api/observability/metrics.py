"""Prometheus metrics."""

from __future__ import annotations

from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter("cirda_http_requests_total", "HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("cirda_http_request_duration_seconds", "HTTP latency", ["method", "path"])
INGEST_EVENTS = Counter("cirda_ingest_events_total", "Ingested evidence events", ["created"])
DECISIONS = Counter("cirda_decisions_total", "Decisions evaluated", ["verdict"])


def metrics_payload() -> bytes:
    return generate_latest()
