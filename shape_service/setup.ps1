# CLIP Shape Detection - Quick Setup and Test
# Run this in PowerShell to set up and test the service

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   CLIP Shape Detection - Quick Setup                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app\services\shape_predict.py")) {
    Write-Host "❌ Error: Not in the correct directory" -ForegroundColor Red
    Write-Host "   Please run this from: ganithamithura\shape_service\" -ForegroundColor Yellow
    exit 1
}

Write-Host "📂 Working Directory: $PWD" -ForegroundColor Green
Write-Host ""

# Step 1: Install dependencies
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 1: Install Dependencies" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
$response = Read-Host "Install/Update dependencies? (Y/n)"
if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    Write-Host "📦 Installing..." -ForegroundColor Cyan
    python -m pip install -e .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Installation failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 2: Test CLIP model
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 2: Test CLIP Model" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
$response = Read-Host "Run CLIP detection test? (Y/n)"
if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    Write-Host "🧪 Testing CLIP model..." -ForegroundColor Cyan
    Write-Host "   (First run will download ~600MB model)" -ForegroundColor Yellow
    python test_clip_detection.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Model test passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Test completed with issues" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 3: Start service
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 3: Start Service" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
$response = Read-Host "Start the shape service? (Y/n)"
if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "🚀 Starting Shape Service on http://localhost:8002" -ForegroundColor Green
    Write-Host "   Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   API Endpoint: POST /detect-shape/" -ForegroundColor Cyan
    Write-Host "   Health Check: GET /" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    try {
        uvicorn app.main:app --reload --port 8002
    }
    catch {
        Write-Host ""
        Write-Host "✅ Service stopped" -ForegroundColor Green
    }
    
    exit 0
}

# Final instructions
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Setup Complete!                                        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Start service:" -ForegroundColor White
Write-Host "   uvicorn app.main:app --reload --port 8002" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Test API:" -ForegroundColor White
Write-Host "   python test_api.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Test with Flutter camera app" -ForegroundColor White
Write-Host ""
Write-Host "4. Read documentation:" -ForegroundColor White
Write-Host "   - IMPLEMENTATION_COMPLETE.md" -ForegroundColor Cyan
Write-Host "   - CLIP_IMPLEMENTATION_README.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Supported Shapes:" -ForegroundColor Yellow
Write-Host "• 2D: Circle, Square, Triangle, Rectangle, Oval, Pentagon, Hexagon" -ForegroundColor White
Write-Host "• 3D: Cube, Sphere, Cone, Cylinder" -ForegroundColor White
Write-Host ""
