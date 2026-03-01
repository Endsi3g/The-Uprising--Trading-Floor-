# install.ps1 - Native Windows Installation Script for Hummingbot
$ErrorActionPreference = "Stop"

Write-Host "--- Initializing Windows Installation ---" -ForegroundColor Cyan

# 1. Detect Conda
$condaExe = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaExe) {
    # Try common paths if not in PATH
    $commonPaths = @(
        "$env:USERPROFILE\anaconda3\Scripts\conda.exe",
        "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
        "C:\ProgramData\Anaconda3\Scripts\conda.exe",
        "C:\ProgramData\Miniconda3\Scripts\conda.exe"
    )
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            $condaExe = $path
            break
        }
    }
}

if (-not $condaExe) {
    Write-Host "Error: Conda not found. Please install Anaconda or Miniconda first." -ForegroundColor Red
    exit 1
}

Write-Host "Using Conda: $condaExe" -ForegroundColor Gray

# 2. Environment Setup
$envName = "hummingbot"
$envFile = "setup/environment.yml"

Write-Host "Checking for '$envName' environment..." -ForegroundColor Cyan
$envList = conda env list | Out-String
if ($envList -match "^$envName\s") {
    Write-Host "Updating existing environment..." -ForegroundColor Yellow
    conda env update -f $envFile
}
else {
    Write-Host "Creating new environment..." -ForegroundColor Yellow
    conda env create -f $envFile
}

# 3. Pip Packages
Write-Host "Installing additional pip dependencies..." -ForegroundColor Cyan
# We assume the environment will be activated by the user later, 
# but for installation we can use python from the environment path
$envPath = (conda env list | Select-String -Pattern "^$envName\s" | ForEach-Object { ($_ -split '\s+')[1] })
if (-not $envPath) { $envPath = (conda env list | Select-String -Pattern "$envName") } # Fallback

$pythonExe = Join-Path $envPath "python.exe"
& $pythonExe -m pip install --no-deps -r setup/pip_packages.txt

# 4. Pre-commit
& $pythonExe -m pip install pre-commit
& $pythonExe -m pre_commit install

Write-Host "`nMISSION ACCOMPLISHED: Installation complete." -ForegroundColor Green
Write-Host "To start Hummingbot, run: conda activate $envName; .\bin\start.ps1" -ForegroundColor Gray
