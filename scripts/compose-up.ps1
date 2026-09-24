# CIRDA Docker Compose bootstrap — lite stack by default (Postgres + API + Web).
param(
    [ValidateSet("lite", "full", "dev")]
    [string]$Profile = "lite",
    [switch]$NoSeed,
    [switch]$NoBuild,
    [switch]$Down
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Require-Command($Name) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' not found on PATH."
    }
}

function Test-DockerReady {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = "SilentlyContinue"
    $out = docker info 2>&1
    $ErrorActionPreference = $prev
    return $LASTEXITCODE -eq 0
}

function Wait-ForHttp($Url, [int]$Attempts = 60) {
    for ($i = 0; $i -lt $Attempts; $i++) {
        foreach ($path in @("/api/v1/health", "/healthz", "/health")) {
            try {
                $resp = Invoke-WebRequest -Uri "$Url$path" -UseBasicParsing -TimeoutSec 3
                if ($resp.StatusCode -eq 200) {
                    return $path
                }
            } catch {
                # retry
            }
        }
        Start-Sleep -Seconds 2
    }
    throw "Service did not become healthy at $Url"
}

function Wait-ForComposeService($ComposeFile, $Service, [int]$Attempts = 60) {
    for ($i = 0; $i -lt $Attempts; $i++) {
        $status = docker compose -f $ComposeFile ps --format json $Service 2>$null
        if ($status) {
            $rows = @($status | ConvertFrom-Json)
            foreach ($row in $rows) {
                if ($row.Service -eq $Service -and $row.Health -eq "healthy") {
                    return
                }
                if ($row.Service -eq $Service -and [string]::IsNullOrEmpty($row.Health) -and $row.State -eq "running") {
                    return
                }
            }
        }
        Start-Sleep -Seconds 2
    }
    throw "Compose service '$Service' did not become healthy"
}

Require-Command docker

if (-not (Test-DockerReady)) {
    Write-Host "ERROR: Docker is not running. Start Docker Desktop and retry." -ForegroundColor Red
    exit 1
}

$composeFile = switch ($Profile) {
    "lite" { "deploy/docker/docker-compose.lite.yml" }
    "full" { "deploy/docker/docker-compose.yml" }
    "dev" { "deploy/docker/docker-compose.dev.yml" }
}

if ($Down) {
    Write-Host "==> Stopping compose stack ($Profile)"
    docker compose -f $composeFile down
    exit 0
}

$buildArgs = @("compose", "-f", $composeFile, "up", "-d")
if (-not $NoBuild) {
    $buildArgs += "--build"
}

Write-Host "==> Starting CIRDA compose profile: $Profile"
Write-Host "    File: $composeFile"
docker @buildArgs
if ($LASTEXITCODE -ne 0) {
    throw "docker compose up failed"
}

Write-Host "==> Waiting for Postgres"
Wait-ForComposeService $composeFile "postgres"

Write-Host "==> Waiting for API"
Wait-ForComposeService $composeFile "api"

$apiUrl = if ($env:CIRDA_API_URL) { $env:CIRDA_API_URL } else { "http://localhost:8000" }
$healthPath = Wait-ForHttp $apiUrl
Write-Host "==> API healthy via $healthPath"

if ($Profile -ne "dev") {
    Write-Host "==> Waiting for Web"
    Wait-ForComposeService $composeFile "web"
}

if (-not $NoSeed) {
    Require-Command uv
    $env:CIRDA_ENV = "local"
    $env:CIRDA_APP_ENV = "development"
    Write-Host "==> Seeding demo estate via HTTP"
    uv run python scripts/seed_demo_estate.py --api-url $apiUrl
    if ($LASTEXITCODE -ne 0) {
        throw "Seed script failed with exit code $LASTEXITCODE"
    }
}

$webUrl = if ($Profile -eq "dev") { "http://localhost:5173" } else { "http://localhost:3000" }

Write-Host ""
Write-Host "==> CIRDA stack is up ($Profile)"
Write-Host "    API:  $apiUrl/api/v1/health"
Write-Host "    Web:  $webUrl"
Write-Host "    Docs: $apiUrl/docs"
Write-Host ""
Write-Host "Stop stack:"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts/compose-up.ps1 -Profile $Profile -Down"
