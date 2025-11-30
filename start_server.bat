@echo off
REM Parking Management System - Backend Server Launcher
REM This script runs the backend server using the conda environment

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ============================================================
echo Parking Management System - Backend Server
echo ============================================================
echo.
echo Environment: parking (Python 3.10.19)
echo.

REM Run the server
C:\Users\Danix\anaconda3\Scripts\conda.exe run -n parking python run_server.py %*

if errorlevel 1 (
    echo.
    echo Error: Failed to start server
    echo.
    pause
    exit /b 1
)

pause
