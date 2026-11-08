@echo off
echo ========================================================
echo Starting ShieldPlus AI Fraud Detection Engine...
echo ========================================================

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" run.py
) ELSE IF EXIST "C:\Users\ddas2\AppData\Local\Python\pythoncore-3.11-64\python.exe" (
    "C:\Users\ddas2\AppData\Local\Python\pythoncore-3.11-64\python.exe" run.py
) ELSE (
    python run.py
)

pause
