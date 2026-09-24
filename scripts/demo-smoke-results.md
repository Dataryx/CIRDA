# Demo smoke results

## Live stack (memory store / `dev-lite`)

| Check | Result |
|-------|--------|
| API `/api/v1/health` | PASS |
| Seed (HTTP `--force`) | PASS — 10 entities, 15 events, channel health |
| `invoice-reconciler-agent` | **UNSAFE** |
| `legacy-csv-export-agent` | **SAFE** |
| `vendor-risk-agent` | **INDETERMINATE** (target-scoped silent DB/messaging → C ≈ 0.73) |

## Playwright E2E (live API, no MSW)

`PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm e2e` → **11 passed** (including axe WCAG serious/critical = 0).

Covered: overview, topology, UNSAFE / INDETERMINATE / SAFE decommission, evidence, coverage, benchmark synthetic banner, a11y landmarks + axe.

## Benchmark gates

- CIRDA `false_safe == 0.000` at m ∈ {0.30, 0.45, 0.60} — **exact**
- Table II: **33/60** metrics within tolerance; remaining gaps documented in `packages/cirda-bench/CALIBRATION.md` (no golden overlays)
- CIRDA decision_coverage within tolerance at all three report losses; CIRDA m=0.30 fully within tolerance

## Docker Compose (Postgres)

Requires Docker Desktop running:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1
# Web http://localhost:3000  API http://localhost:8000
```

Lite profile: Postgres + Redis + API + Web. Migrations run on API start; seed runs after health.

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
