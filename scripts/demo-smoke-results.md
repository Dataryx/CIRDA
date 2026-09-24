# Demo smoke results

## Live stack (memory store)

| Check | Result |
|-------|--------|
| API `/api/v1/health` | PASS |
| Seed (HTTP `--force`) | PASS — 10 entities, 15 events, channel health |
| `invoice-reconciler-agent` | **UNSAFE** (coverage 1.0) |
| `legacy-csv-export-agent` | **SAFE** (coverage 1.0) |
| `vendor-risk-agent` | **INDETERMINATE** (coverage ≈0.727, target-scoped silent DB/messaging) |

## Playwright E2E (live API, no MSW)

`PLAYWRIGHT_SKIP_WEBSERVER=1 pnpm e2e` → **10 passed, 1 skipped** (axe soft-skip until `@axe-core/playwright` is installed).

Covered: overview, topology, UNSAFE / INDETERMINATE / SAFE decommission paths, evidence drilldown, coverage, benchmark synthetic banner, a11y landmarks.

## How to reproduce

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev-lite.ps1
# or manually:
#   API + seed already documented in README
cd apps/web
$env:PLAYWRIGHT_SKIP_WEBSERVER = '1'
pnpm e2e
```
