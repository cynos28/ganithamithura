# Start all Ganithamithura services through API Gateway
# This script ensures all dependencies are properly configured

Write-Host "Starting Ganithamithura API Gateway with all services" -ForegroundColor Green
Write-Host ""

# Get the api-gateway directory
$apiGatewayDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $apiGatewayDir

Write-Host "Project Root: $projectRoot" -ForegroundColor Cyan
Write-Host "API Gateway: $apiGatewayDir" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include project root for 'common' module
$env:PYTHONPATH = "$projectRoot;$env:PYTHONPATH"

# Navigate to api-gateway directory
Set-Location $apiGatewayDir

Write-Host "Syncing dependencies..." -ForegroundColor Yellow
uv sync

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies synced successfully" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting API Gateway on http://localhost:8000" -ForegroundColor Green
    Write-Host ""
    Write-Host "Available endpoints:" -ForegroundColor Cyan
    Write-Host "   - API Gateway:        http://localhost:8000" -ForegroundColor White
    Write-Host "   - Docs (Swagger):     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   - Auth Service:       http://localhost:8000/auth" -ForegroundColor White
    Write-Host "   - Shape Service:      http://localhost:8000/shapes-patterns" -ForegroundColor White
    Write-Host ""
    Write-Host "Shape Detection Endpoint:" -ForegroundColor Yellow
    Write-Host "   POST http://localhost:8000/shapes-patterns/detect-shape" -ForegroundColor White
    Write-Host ""
    Write-Host "Press CTRL+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Start the server
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}
else {
    Write-Host "Failed to sync dependencies" -ForegroundColor Red
    Write-Host "   Please check the error messages above" -ForegroundColor Yellow
    exit 1
}

