# CIRDA monorepo bootstrap (Windows PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Require-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' not found on PATH."
    }
}

Write-Host "==> Checking prerequisites"
Require-Command uv
Require-Command pnpm

Write-Host "==> Syncing Python workspace"
uv sync --all-packages --group dev

Write-Host "==> Installing pre-commit hooks"
try { uv run pre-commit install } catch { Write-Warning "pre-commit install skipped" }

Write-Host "==> Installing frontend dependencies"
Push-Location apps/web
pnpm install
Pop-Location

if (-not (Test-Path .env)) {
    Write-Host "==> Creating .env from .env.example"
    Copy-Item .env.example .env
}

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "  Start API:  cd apps/api; uv run uvicorn cirda_api.asgi:app --reload --port 8000"
Write-Host "  Start Web:  cd apps/web; pnpm dev"
Write-Host "  Seed demo:  uv run python scripts/seed_demo_estate.py"
