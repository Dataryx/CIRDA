# Demo smoke results

## Live stack (Compose lite / Postgres)

| Check | Result |
|-------|--------|
| API `/api/v1/health` | PASS |
| Seed (HTTP `--force`) | PASS — idempotent re-ingest (duplicate `event_id` → `created=false`) |
| `invoice-reconciler-agent` | **UNSAFE** |
| `legacy-csv-export-agent` | **SAFE** |
| `vendor-risk-agent` | **INDETERMINATE** (target-scoped silent DB/messaging → C ≈ 0.73) |

## Playwright E2E (live Compose web + API)

```powershell
$env:PLAYWRIGHT_SKIP_WEBSERVER = '1'
$env:PLAYWRIGHT_BASE_URL = 'http://localhost:3000'
$env:CIRDA_API_URL = 'http://localhost:8000'
pnpm e2e
```

→ **11 passed** (including axe WCAG serious/critical = 0).

Covered: overview, topology, UNSAFE / INDETERMINATE / SAFE decommission, evidence, coverage, benchmark synthetic banner, a11y landmarks + axe.

## Benchmark gates

- CIRDA `false_safe == 0.000` at m ∈ {0.30, 0.45, 0.60} — **exact**
- Table II: **35/60** metrics within tolerance; remaining gaps documented in `packages/cirda-bench/CALIBRATION.md` (no golden overlays)
- CIRDA blast_precision at m=0.60 remains a residual (bp↔br tradeoff under blast-graph confidence filter)
- CIRDA decision_coverage within tolerance at all three report losses; CIRDA m=0.30 fully within tolerance

## Docker Compose (Postgres)

Requires Docker Desktop running:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1
# Web http://localhost:3000  API http://localhost:8000
```

Lite profile: Postgres + Redis + API + Web. Migrations run on API start; seed after health.

## How to reproduce (memory)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev-lite.ps1
# or: API on :8000 + web on :5173 + seed_demo_estate.py

cd apps/web
$env:PLAYWRIGHT_SKIP_WEBSERVER = '1'
pnpm e2e

# from repo root
powershell -ExecutionPolicy Bypass -File scripts/verify.ps1
```
