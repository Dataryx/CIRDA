# Incident: Telemetry Suppression

## Overview

Telemetry suppression occurs when an evidence channel stops delivering events while dependencies still exist. CIRDA detects this via coverage suppression logic and channel health endpoints.

## Detection

- `suppressed_channels` non-empty in coverage estimate
- Messaging channel declared (static) but no recent trace/messaging events
- Ingest dashboard: DLQ spike or consumer lag

## Demo Scenario

The demo estate (`make seed`) includes:

- Static declaration: `invoice-reconciler-agent → invoice-queue` (60 days old)
- No recent messaging events on that channel
- Trace events continue on other edges

This simulates partial observability — decisions may be INDETERMINATE for entities relying on suppressed channels.

## Response

### Immediate (0–15 min)

1. Confirm ingest worker health: `GET http://localhost:8081/health`
2. Check Kafka lag (full stack): Grafana `cirda-ingest` dashboard
3. Verify no network policy blocking telemetry producers

### Short-term (15–60 min)

1. Enable fallback channel if configured (`CIRDA_KAFKA_AUTO_FALLBACK=true`)
2. Replay buffered telemetry: `python scripts/replay_telemetry.py data/replay.jsonl`
3. Mark incident in audit log

### Recovery Validation

1. `GET /api/v1/coverage/channel-health` — all active channels green
2. Re-run affected decisions
3. Confirm `suppressed_channels` empty

## Communication Template

> CIRDA coverage dropped due to suppressed `{channel}` telemetry affecting `{entity_count}` entities. Decisions may return INDETERMINATE until coverage restores. Do not proceed with retirements.

## Post-Incident

- Add monitor on `sum(cirda_coverage_suppressed_channels) > 0`
- Review static declarations vs live instrumentation gaps
