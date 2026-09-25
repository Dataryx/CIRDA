# Demo smoke results

## Live stack (Compose full)

| Check | Result |
|-------|--------|
| API `/api/v1/health` | PASS |
| Ingest `/health` (Kafka mode) | PASS — `kafka_connected=true` |
| OTel collector | PASS (debug exporter) |
| Seed (HTTP) | PASS |
| Kafka → ingest → Postgres | PASS — `events_processed=3`, consumer lag 0 |
| `invoice-reconciler-agent` | **UNSAFE** |
| `legacy-csv-export-agent` | **SAFE** |
| `vendor-risk-agent` | **INDETERMINATE** (C ≈ 0.73) |

```powershell
powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1 -Profile full
# Produce smoke events via rpk inside Redpanda (host clients: localhost:19092):
docker exec -i docker-redpanda-1 sh -c "tr -d '\r' < /tmp/smoke.jsonl | rpk topic produce cirda.evidence.raw"
```

## Playwright E2E (Compose web + API)

```powershell
$env:PLAYWRIGHT_SKIP_WEBSERVER = '1'
$env:PLAYWRIGHT_BASE_URL = 'http://localhost:3000'
$env:CIRDA_API_URL = 'http://localhost:8000'
$env:CI = '1'
pnpm e2e
```

→ **11 passed** (including axe WCAG serious/critical = 0).

## Benchmark gates

- CIRDA `false_safe == 0.000` at m ∈ {0.30, 0.45, 0.60} — **exact**
- Table II: **35/60** metrics within tolerance; remaining gaps in `packages/cirda-bench/CALIBRATION.md`
- CIRDA blast_precision at m=0.60 remains a residual (bp↔br tradeoff)

## Compose profiles

```powershell
powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1 -Profile lite   # Postgres+Redis+API+Web
powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1 -Profile full   # + Redpanda + ingest + OTel
```

- Full: Web http://localhost:3000 · API :8000 · Ingest :8081 · Kafka EXTERNAL :19092
- Host Kafka clients must use `localhost:19092` (in-cluster uses `redpanda:9092`)

## How to reproduce (memory / lite)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev-lite.ps1
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```
