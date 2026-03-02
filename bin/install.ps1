# install.ps1 - Native Windows Installation Script for Hummingbot
$ErrorActionPreference = "Stop"

Write-Host "--- Initializing Windows Installation ---" -ForegroundColor Cyan

# 1. Detect Conda
$condaExeInfo = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaExeInfo) {
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
else {
    $condaExe = $condaExeInfo.Path
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
$envList = & $condaExe env list
# Per-line match for exact name at start of line
$environmentExists = $envList | Select-String -Pattern "^\s*$envName\b"

try {
    if ($environmentExists) {
        Write-Host "Updating existing environment..." -ForegroundColor Yellow
        & $condaExe env update -f $envFile
    }
    else {
        Write-Host "Creating new environment..." -ForegroundColor Yellow
        & $condaExe env create -f $envFile
    }
}
catch {
    $err = $_.ToString()
    if ($err -match "InvalidArchiveError") {
        Write-Host "`n[CRITICAL] Conda detected corrupted archives (InvalidArchiveError)." -ForegroundColor Red
        Write-Host "Please run the following command to clear the cache and try again:" -ForegroundColor Yellow
        Write-Host "   conda clean --all" -ForegroundColor Cyan
    }
    throw $_
}

# 3. Pip Packages
Write-Host "Installing additional pip dependencies..." -ForegroundColor Cyan

# Robustly extract path using line-based parsing
# Standard output line: [Name] [Mode] [Path]
# Or just [Path] for nameless envs
# Example line: hummingbot            *  C:\Users\upris\.conda\envs\hummingbot
$matchingLine = $envList | Select-String -Pattern "^\s*$envName\b" | Select-Object -First 1 -ExpandProperty Line
if ($matchingLine) {
    # Extract path: it's the last part of the line separated by whitespace
    $envPath = ($matchingLine -split '\s+')[-1]
}

if (-not $envPath) {
    Write-Host "Error: Could not find path for environment '$envName'." -ForegroundColor Red
    exit 1
}

$pythonExe = Join-Path $envPath "python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Error: Python executable not found at $pythonExe." -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $pythonExe" -ForegroundColor Gray

# 4. Link package and install dependencies
Write-Host "Linking package and installing dependencies..." -ForegroundColor Cyan
& $condaExe run -n $envName conda develop .
& $condaExe run -n $envName python -m pip install --no-deps -r setup/pip_packages.txt

# 5. Build Cython extensions
Write-Host "Building Cython extensions (this may take a few minutes)..." -ForegroundColor Cyan
& $condaExe run -n $envName --no-capture-output python setup.py build_ext --inplace

# 6. Pre-commit
& $condaExe run -n $envName python -m pip install pre-commit
& $condaExe run -n $envName pre-commit install

Write-Host "`nMISSION ACCOMPLISHED: Installation complete." -ForegroundColor Green
Write-Host "To start Hummingbot, run: conda activate $envName; .\bin\start.ps1" -ForegroundColor Gray
