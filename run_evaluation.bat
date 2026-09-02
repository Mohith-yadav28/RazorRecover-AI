@echo off
title RazorRecover AI - Benchmark Evaluation
cd /d "%~dp0"
set PYTHONPATH=backend
echo Running Experimental Benchmark Evaluation Script...
"C:\Users\HP\AppData\Local\Programs\Python\Python313\python.exe" scripts/run_evaluation.py
pause
