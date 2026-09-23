# ADR 0003: At-Least-Once Idempotent Ingestion

## Status

Accepted

## Context

Telemetry sources (Kafka, HTTP) may deliver duplicates or retries. Re-processing
must not inflate observation counts or create duplicate entities.

## Decision

Ingest is **at-least-once** with **idempotent deduplication**:

- HTTP: `Idempotency-Key` header or body field
- Events: `payload_hash` + source marker for dedup
- Failed Kafka messages → DLQ (`CIRDA_KAFKA_DLQ_TOPIC`)

## Consequences

- **Positive:** Safe retries; reproducible graph state
- **Negative:** Requires idempotency key discipline from producers
- **Testing:** ingest integration tests assert `created: false` on replay
