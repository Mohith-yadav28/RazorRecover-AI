@echo off
title RazorRecover AI - FastAPI Backend Server
cd /d "%~dp0"
set PYTHONPATH=backend
echo Starting RazorRecover AI FastAPI Backend Server on http://localhost:8000 ...
"C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" -m uvicorn app.main:app --reload --port 8000
pause
