# Pipeline

The CIRDA pipeline moves evidence from telemetry sources through normalization,
graph inference, coverage estimation, and tri-state gating.

## Stages

```mermaid
flowchart LR
  Sources[Telemetry sources] --> Ingest[Ingest / normalize]
  Ingest --> Fusion[Multi-channel fusion]
  Fusion --> Layers[G_c / G_p layering]
  Layers --> Coverage[Coverage C]
  Coverage --> Gate[Tri-state gate]
  Gate --> Report[Decision report]
```

## Ingest

The ingest worker (`apps/ingest-worker`) and API ingest routes share normalization
logic from `cirda-core`.

| Adapter | Channel |
|---------|---------|
| TraceAdapter | trace |
| DatabaseAdapter | database |
| MessagingAdapter | messaging |
| IamAdapter | iam |
| AgentFrameworkAdapter | agent_framework |
| StaticAdapter | static_declared |

## Event bus modes

| Mode | Config | Use case |
|------|--------|----------|
| inmemory | `CIRDA_EVENT_BUS=inmemory` | dev, unit tests |
| redis | `CIRDA_EVENT_BUS=redis` | single-region pub/sub |
| kafka | `CIRDA_EVENT_BUS=kafka` | high-volume telemetry |

## Batching and idempotency

- Batch limits: `CIRDA_BATCH_MAX_EVENTS` (500), `CIRDA_BATCH_MAX_WAIT_MS` (200)
- HTTP ingest accepts `Idempotency-Key`; duplicates return `created: false`
- Failed Kafka messages route to `CIRDA_KAFKA_DLQ_TOPIC`

See [ADR 0003](../adr/0003-at-least-once-idempotent-ingestion.md).
