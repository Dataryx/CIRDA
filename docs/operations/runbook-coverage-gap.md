# Runbook: Coverage Gap (INDETERMINATE)

## Trigger

Decision verdict is **INDETERMINATE** with reason code indicating coverage below `C_MIN` (default 0.85).

## Symptoms

- `coverage < C_MIN` in decision report
- `meets_threshold: false` on `GET /api/v1/coverage`
- Elevated INDETERMINATE rate on Grafana `cirda-decisions` dashboard

## Diagnosis

1. Check global coverage:
   ```bash
   curl http://localhost:8000/api/v1/coverage -H "Authorization: Bearer dev"
   ```

2. Inspect channel health:
   ```bash
   curl http://localhost:8000/api/v1/coverage/channel-health -H "Authorization: Bearer dev"
   ```

3. Identify suppressed channels in `suppressed_channels` list.

## Remediation

| Gap Type | Action |
|----------|--------|
| Missing trace instrumentation | Enable OTel export to ingest worker OTLP port |
| Stale messaging events | Verify Kafka topic lag; check [incident-telemetry-suppression.md](incident-telemetry-suppression.md) |
| Ambiguous entity identity | Resolve aliases in entity metadata; re-ingest with canonical IDs |
| New agent (cold start) | Wait for observation window or ingest static declarations |

## Re-evaluation Criteria

Re-run decision when:

- `coverage >= C_MIN`
- `observed_entities / total_entities` stable for 1h
- No active suppression incidents

## Prevention

- Alert when `cirda_coverage_at_decision` drops below 0.85 (see Grafana dashboard)
- Schedule weekly coverage snapshots (`CIRDA_SNAPSHOT_JOB_INTERVAL_SECONDS`)
