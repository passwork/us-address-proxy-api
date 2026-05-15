$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$VenvDir = Join-Path $ProjectDir "venv"

Write-Host "=== US Address Proxy Service Setup ===" -ForegroundColor Cyan

# 1. Create virtual environment
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
} else {
    Write-Host "Virtual environment already exists."
}

# 2. Activate and install dependencies
Write-Host "Installing dependencies..."
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
& $ActivateScript

python -m pip install --upgrade pip
python -m pip install -r (Join-Path $ProjectDir "requirements.txt")

# 3. Run tests
Write-Host "Running tests..."
Set-Location $ProjectDir
pytest -v

Write-Host ""
Write-Host "=== Setup complete ===" -ForegroundColor Green
Write-Host "To activate the environment: .\venv\Scripts\Activate.ps1"
Write-Host "To start the server: uvicorn app.main:app --reload --port 8000"
