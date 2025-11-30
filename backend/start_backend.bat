@echo off
REM Parking Management System - Backend Server Launcher
REM Uses the local backend venv environment

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo Parking Management System - Backend Server
echo ============================================================
echo.
echo Environment: backend\venv (Python 3.10.19)
echo.

REM Run the server using the backend venv
C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python run_backend.py %*

if errorlevel 1 (
    echo.
    echo Error: Failed to start server
    echo.
    pause
    exit /b 1
)

pause
