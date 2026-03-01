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

# Check if environment is activated
if ($env:CONDA_DEFAULT_ENV -ne "hummingbot") {
    Write-Host "Error: 'hummingbot' conda environment is not activated." -ForegroundColor Red
    Write-Host "Please run: conda activate hummingbot" -ForegroundColor Yellow
    exit 1
}

# Build command parts
$argsList = @("bin/hummingbot_quickstart.py")
if ($p) { $argsList += "-p", "`"$p`"" }
if ($f) {
    if ($f -match "\.(yml|py)$") {
        $argsList += "-f", "`"$f`""
    }
    else {
        Write-Host "Error: File must be .yml or .py" -ForegroundColor Red
        exit 1
    }
}
if ($c) {
    if ($c -match "\.yml$") {
        $argsList += "-c", "`"$c`""
    }
    else {
        Write-Host "Error: Config must be .yml" -ForegroundColor Red
        exit 1
    }
}

# Run
python $argsList
