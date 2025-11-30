# Start Django Server with Virtual Environment
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Starting Django API Server with YOLO Integration" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
$venvPath = Join-Path $PSScriptRoot "DjangoEnv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    Write-Host "Activating Django environment..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "Error: Virtual environment not found at $venvPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Available endpoints:" -ForegroundColor Yellow
Write-Host "  - POST /api/detect-plate/     (Detect plate only)" -ForegroundColor White
Write-Host "  - POST /api/detect-entry/     (Detect and register entry)" -ForegroundColor White
Write-Host "  - POST /api/detect-exit/      (Detect and register exit)" -ForegroundColor White
Write-Host "  - GET  /api/status/           (Get parking status)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Start Django server
python manage.py runserver 8000
