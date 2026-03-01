# ship.ps1 - Native Windows Shipping Wrapper
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "THE UPRISING : SHIPPING AUTOMATION" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$pythonPath = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

python ship.py
