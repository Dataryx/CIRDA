# CIRDA dev-lite: in-memory API + Vite web + demo seed (no Postgres/Redis).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Require-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' not found on PATH."
    }
}

function Wait-ForApi($Url, $Attempts = 30) {
    for ($i = 0; $i -lt $Attempts; $i++) {
        foreach ($path in @("/healthz", "/api/v1/health", "/health")) {
            try {
                $resp = Invoke-WebRequest -Uri "$Url$path" -UseBasicParsing -TimeoutSec 2
                if ($resp.StatusCode -eq 200) {
                    return $path
                }
            } catch {
                # retry
            }
        }
        Start-Sleep -Seconds 1
    }
    throw "API did not become healthy at $Url"
}

Require-Command uv
Require-Command pnpm

$env:CIRDA_ENV = "local"
$env:CIRDA_MEMORY_STORE = "true"
$env:CIRDA_EVENT_BUS = "inmemory"
$env:CIRDA_AUTH_MODE = "dev"
$env:CIRDA_SCHEDULER_ENABLED = "false"
$env:CIRDA_APP_ENV = "development"

$apiUrl = if ($env:CIRDA_API_URL) { $env:CIRDA_API_URL } else { "http://localhost:8000" }
$webUrl = if ($env:PLAYWRIGHT_BASE_URL) { $env:PLAYWRIGHT_BASE_URL } else { "http://localhost:5173" }

Write-Host "==> Starting CIRDA dev-lite (memory store, dev auth)"
Write-Host "    API: $apiUrl"
Write-Host "    Web: $webUrl"

$apiProc = Start-Process -FilePath "uv" `
    -ArgumentList @("run", "uvicorn", "cirda_api.asgi:app", "--host", "0.0.0.0", "--port", "8000") `
    -WorkingDirectory "$Root\apps\api" `
    -PassThru `
    -WindowStyle Hidden

try {
    $healthPath = Wait-ForApi $apiUrl
    Write-Host "==> API healthy via $healthPath"

    Write-Host "==> Seeding demo estate via HTTP"
    uv run python scripts/seed_demo_estate.py --api-url $apiUrl
    if ($LASTEXITCODE -ne 0) {
        throw "Seed script failed with exit code $LASTEXITCODE"
    }

    $webProc = Start-Process -FilePath "pnpm" `
        -ArgumentList @("dev", "--host", "127.0.0.1", "--port", "5173") `
        -WorkingDirectory "$Root\apps\web" `
        -PassThru `
        -WindowStyle Hidden

    Write-Host ""
    Write-Host "==> dev-lite is running"
    Write-Host "    API:  $apiUrl/api/v1/health"
    Write-Host "    Web:  $webUrl"
    Write-Host ""
    Write-Host "Run Playwright E2E (live API, no MSW):"
    Write-Host "  cd apps/web"
    Write-Host "  `$env:PLAYWRIGHT_SKIP_WEBSERVER='1'"
    Write-Host "  pnpm e2e"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop API (PID $($apiProc.Id)) and Web (PID $($webProc.Id))."

    try {
        while ($true) {
            Start-Sleep -Seconds 5
            if ($apiProc.HasExited) {
                throw "API process exited unexpectedly (code $($apiProc.ExitCode))."
            }
            if ($webProc.HasExited) {
                throw "Web process exited unexpectedly (code $($webProc.ExitCode))."
            }
        }
    } finally {
        if (-not $webProc.HasExited) {
            Stop-Process -Id $webProc.Id -Force -ErrorAction SilentlyContinue
        }
    }
} finally {
    if (-not $apiProc.HasExited) {
        Stop-Process -Id $apiProc.Id -Force -ErrorAction SilentlyContinue
    }
}
