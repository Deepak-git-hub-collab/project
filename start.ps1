# ShieldPlus AI PowerShell Launcher
$ErrorActionPreference = "Continue"

try {
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force -ErrorAction SilentlyContinue
} catch {}

$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } elseif ($MyInvocation.MyCommand.Path) { Split-Path -Parent $MyInvocation.MyCommand.Path } else { (Get-Location).Path }
Set-Location $ScriptDir

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Starting ShieldPlus AI Fraud Detection Engine...     " -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan

$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
$GlobalPython = "C:\Users\ddas2\AppData\Local\Python\pythoncore-3.11-64\python.exe"

$PythonExe = $null
if (Test-Path $VenvPython) {
    $PythonExe = $VenvPython
} elseif (Test-Path $GlobalPython) {
    $PythonExe = $GlobalPython
} else {
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -notmatch 'WindowsApps') {
        $PythonExe = $cmd.Source
    }
}

if (-not $PythonExe) {
    Write-Host "[!] Error: Could not locate Python 3.11." -ForegroundColor Red
    Write-Host "    Please ensure .venv exists or Python is installed." -ForegroundColor Yellow
    Exit 1
}

Write-Host "[*] Using Python: $PythonExe" -ForegroundColor Green
Write-Host "[*] Starting server on http://127.0.0.1:8000 (Ctrl+C to stop)" -ForegroundColor Green

& $PythonExe run.py
