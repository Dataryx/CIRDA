# CIRDA Windows verification (mirrors `make verify`)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> constants parity"
uv run python scripts/check_constants_parity.py

Write-Host "==> cirda-core tests"
uv run pytest packages/cirda-core/tests -q --tb=line

Write-Host "==> cirda-bench safety + determinism"
uv run pytest packages/cirda-bench/tests/test_zero_false_safe_at_30_45_60_loss.py `
  packages/cirda-bench/tests/test_determinism.py `
  packages/cirda-bench/tests/test_no_metric_overlay.py `
  packages/cirda-bench/tests/test_generator_shape.py `
  packages/cirda-bench/tests/test_scalability_shape.py `
  packages/cirda-bench/tests/test_cirda_core_integration.py -q --tb=line

Write-Host "==> cirda-bench Table II (xfails document remaining calibration gaps)"
uv run pytest packages/cirda-bench/tests/test_reproduces_table_ii.py -q --tb=line

Write-Host "==> API tests (in-memory)"
$env:CIRDA_MEMORY_STORE = "true"
$env:CIRDA_EVENT_BUS = "inmemory"
$env:CIRDA_AUTH_MODE = "dev"
$env:CIRDA_SCHEDULER_ENABLED = "false"
uv run pytest apps/api/tests -q --tb=line

Write-Host "==> ingest-worker tests"
uv run pytest apps/ingest-worker/tests -q --tb=line

Write-Host "==> frontend vitest"
Push-Location apps/web
pnpm test
Pop-Location

Write-Host "==> verify OK (core safety gates green; see CALIBRATION.md for Table II gaps)"
