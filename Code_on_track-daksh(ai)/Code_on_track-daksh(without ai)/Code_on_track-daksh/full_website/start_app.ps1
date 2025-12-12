$ErrorActionPreference = "Stop"

Write-Host "Starting QrTrack Application..." -ForegroundColor Green

# Path to the full_website directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Start Backend
Write-Host "Launching Backend (FastAPI)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (Test-Path venv) { .\venv\Scripts\activate } else { Write-Warning 'venv not found, running global python' }; uvicorn app.main:app --reload --port 8000"

# Start Frontend
Write-Host "Launching Frontend (Vite)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "------------------------------------------------"
Write-Host "Application launching in separate windows."
Write-Host "Backend API: http://localhost:8000"
Write-Host "Frontend UI: http://localhost:5173 (or similar)"
Write-Host "------------------------------------------------"
