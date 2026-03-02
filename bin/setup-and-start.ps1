# setup-and-start.ps1
# Unified Installer & Launcher for The Uprising Trading Floor
# 
# Usage: .\bin\setup-and-start.ps1 [--desktop] [--clean]

param(
    [switch]$desktop = $false,
    [switch]$clean = $false
)

$ErrorActionPreference = "Stop"
Write-Host "`n--- THE UPRISING: Unified Setup & Launch ---" -ForegroundColor Cyan

$root = Resolve-Path "$PSScriptRoot\.."
$suiteDir = Join-Path $root "trading-ai-suite"
$dashDir = Join-Path $suiteDir "dashboard"

# 0. Clean Cache (Optional)
if ($clean) {
    Write-Host "`n[0/5] Cleaning Conda cache..." -ForegroundColor White
    conda clean --all -y
}

# 1. Core Installation (Hummingbot & Conda)
Write-Host "`n[1/5] Running Core Installation..." -ForegroundColor White
Set-Location $root
.\bin\install.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Installation failed." -ForegroundColor Red
    exit 1
}

# 2. Port Conflict Check (Native Ollama)
Write-Host "`n[2/5] Hardening Port 11434 (Ollama)..." -ForegroundColor White
$portConflict = Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue
if ($portConflict) {
    Write-Host "CONFLICT: Port 11434 is occupied. Terminating blocking processes..." -ForegroundColor Yellow
    taskkill /F /IM ollama.exe /T 2>$null
    Start-Sleep -Seconds 3
    if (Get-NetTCPConnection -LocalPort 11434 -ErrorAction SilentlyContinue) {
        Write-Host "ERROR: Could not clear port 11434. Please close apps manually." -ForegroundColor Red
        exit 1
    }
}

# 3. Suite Environment (.env)
Write-Host "`n[3/5] Checking Suite Environment..." -ForegroundColor White
if (-not (Test-Path "$suiteDir\.env")) {
    Write-Host "Initializing .env from example..." -ForegroundColor Gray
    Copy-Item "$suiteDir\.env.example" "$suiteDir\.env"
    Write-Host "IMPORTANT: Please edit trading-ai-suite\.env with your API keys!" -ForegroundColor Yellow
}

# 4. Orchestrate Backend (Docker)
Write-Host "`n[4/5] Starting Backend Stack (Docker)..." -ForegroundColor White
Set-Location $suiteDir
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Compose failed." -ForegroundColor Red
    exit 1
}

# 5. Launch Dashboard
Write-Host "`n[5/5] Launching Visual Command Center..." -ForegroundColor White
Set-Location $dashDir

# Check node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Dashboard dependencies..." -ForegroundColor Gray
    npm install
}

Write-Host "`n--- MISSION READY ---" -ForegroundColor Cyan
Write-Host "The Trading Floor is now LIVE." -ForegroundColor Gray

if ($desktop) {
    Write-Host "Starting Native Desktop App..." -ForegroundColor Green
    npm run electron-dev
}
else {
    Write-Host "Starting Web Dashboard (http://localhost:3000)..." -ForegroundColor Green
    npm run dev
}
