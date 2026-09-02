# RazorRecover AI — One-Command Windows Quickstart
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting RazorRecover AI Backend & Frontend Servers..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$env:PYTHONPATH="backend"

# Start Backend Server in Background Window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; `$env:PYTHONPATH='backend'; 'C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe' -m uvicorn app.main:app --reload --port 8000"

# Start Frontend Server in Current Window
Set-Location "$PSScriptRoot\frontend"
npm run dev
