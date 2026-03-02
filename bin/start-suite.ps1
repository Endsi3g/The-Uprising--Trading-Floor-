# start-suite.ps1
# Unified launcher for The Uprising Trading Floor
# 
# Usage: .\bin\start-suite.ps1 [--desktop]

param(
    [switch]$desktop = $false
)

$ErrorActionPreference = "Stop"
Write-Host "`n--- Initializing The Uprising Suite ---" -ForegroundColor Cyan

$root = Resolve-Path "$PSScriptRoot\.."
$suiteDir = Join-Path $root "trading-ai-suite"
$dashDir = Join-Path $suiteDir "dashboard"

# 1. Environment Setup
Write-Host "`n[1/3] Checking environment..." -ForegroundColor White
if (-not (Test-Path "$suiteDir\.env")) {
    Write-Host "Creating .env from example..." -ForegroundColor Gray
    Copy-Item "$suiteDir\.env.example" "$suiteDir\.env"
    Write-Host "WARNING: .env created. Please add your API keys to enable real trading." -ForegroundColor Yellow
}
else {
    Write-Host ".env found." -ForegroundColor Gray
}

# 2. Launch Docker Services
Write-Host "`n[2/3] Orchestrating Backend (Docker)..." -ForegroundColor White
Set-Location $suiteDir
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Compose failed. Ensure Docker is running." -ForegroundColor Red
    exit 1
}

# 3. Launch Dashboard
Write-Host "`n[3/3] Launching Dashboard..." -ForegroundColor White
Set-Location $dashDir

# Check node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies (npm install)..." -ForegroundColor Gray
    npm install
}

if ($desktop) {
    Write-Host "Starting Native Desktop App..." -ForegroundColor Green
    npm run electron-dev
}
else {
    Write-Host "Starting Web Dashboard (http://localhost:3000)..." -ForegroundColor Green
    npm run dev
}

Write-Host "`n--- MISSION COMPLETE ---" -ForegroundColor Cyan
