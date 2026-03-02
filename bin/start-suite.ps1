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

# 0. Port Check (Ollama Conflict)
Write-Host "`n[0/3] Checking for port conflicts..." -ForegroundColor White
$portConflict = Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue
if ($portConflict) {
    $proc = Get-Process -Id $portConflict.OwningProcess -ErrorAction SilentlyContinue
    if ($proc.ProcessName -eq "ollama") {
        Write-Host "CONFLICT: Native Ollama is running on port 11434." -ForegroundColor Yellow
        Write-Host "Attempting to stop native Ollama to allow Docker stack to start..." -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force
        Start-Sleep -Seconds 2
    }
    else {
        Write-Host "WARNING: Port 11434 is occupied by $($proc.ProcessName). Docker may fail." -ForegroundColor Yellow
    }
}

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

Write-Host "`n--- MISSION COMPLETE ---" -ForegroundColor Cyan
Write-Host "The Trading Floor is now open. Control the bots via the dashboard." -ForegroundColor Gray

if ($desktop) {
    Write-Host "Starting Native Desktop App..." -ForegroundColor Green
    npm run electron-dev
}
else {
    Write-Host "Starting Web Dashboard (http://localhost:3000)..." -ForegroundColor Green
    npm run dev
}
