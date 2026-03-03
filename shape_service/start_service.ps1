# Start Shape Service with PyTorch Model
# This script sets up the Python path and starts the shape service

Write-Host "🚀 Starting Shape Service with PyTorch Model Integration" -ForegroundColor Green
Write-Host ""

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Add the parent directory to Python path for 'common' module
$env:PYTHONPATH = "$projectRoot;$env:PYTHONPATH"

Write-Host "📁 Project Root: $projectRoot" -ForegroundColor Cyan
Write-Host "📁 Service Directory: $scriptDir" -ForegroundColor Cyan
Write-Host ""

# Navigate to the shape service directory
Set-Location $scriptDir

# Check if virtual environment exists
if (Test-Path ".venv\Scripts\python.exe") {
    Write-Host "✅ Using virtual environment" -ForegroundColor Green
    & .venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
} else {
    Write-Host "⚠️  No virtual environment found, using system Python" -ForegroundColor Yellow
    Write-Host "   Run 'uv sync' to create the virtual environment" -ForegroundColor Yellow
    Write-Host ""
    python -m uvicorn app.main:app --reload --port 8001
}
