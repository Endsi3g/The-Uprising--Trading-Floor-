# start.ps1 - Native Windows Start Script for Hummingbot
param (
    [string]$p = "", # Password
    [string]$f = "", # Strategy or Script file
    [string]$c = ""  # Config file
)

Write-Host "--- Starting Hummingbot (Windows) ---" -ForegroundColor Cyan

# Check if bin/hummingbot_quickstart.py exists
if (-not (Test-Path "bin/hummingbot_quickstart.py")) {
    Write-Host "Error: bin/hummingbot_quickstart.py not found. Run from the project root." -ForegroundColor Red
    exit 1
}

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

# 2. Extract Hummingbot Environment Python Path
$envName = "hummingbot"
$envList = & $condaExe env list
$matchingLine = $envList | Select-String -Pattern "^\s*$envName\b" | Select-Object -First 1 -ExpandProperty Line

if ($matchingLine) {
    # Extract path: it's the last part of the line separated by whitespace
    $envPath = ($matchingLine -split '\s+')[-1]
}

if (-not $envPath) {
    Write-Host "Error: Could not find path for environment '$envName'. Have you run .\bin\install.ps1?" -ForegroundColor Red
    exit 1
}

$pythonExe = Join-Path $envPath "python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Error: Python executable not found at $pythonExe." -ForegroundColor Red
    exit 1
}

# Build command parts
$argsList = @("bin/hummingbot_quickstart.py")
if ($p) { $argsList += "-p", $p }
if ($f) {
    if ($f -match "\.(yml|py)$") {
        $argsList += "-f", $f
    }
    else {
        Write-Host "Error: File must be .yml or .py" -ForegroundColor Red
        exit 1
    }
}
if ($c) {
    if ($c -match "\.yml$") {
        $argsList += "-c", $c
    }
    else {
        Write-Host "Error: Config must be .yml" -ForegroundColor Red
        exit 1
    }
}

# Run
Write-Host "Launching Hummingbot via 'conda run'..." -ForegroundColor Gray
& $condaExe run -n $envName --no-capture-output python $argsList
