@echo off
REM Parking Management System - Master Launcher
REM Allows choosing between backend venv or main parking environment

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo Parking Management System - Launcher
echo ============================================================
echo.
echo Choose environment:
echo   1) Backend venv (Recommended - isolated)
echo   2) Main parking environment
echo   3) Exit
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting with backend venv...
    echo.
    cd /d "%~dp0backend"
    C:\Users\Danix\anaconda3\Scripts\conda.exe run -p venv python run_backend.py
) else if "%choice%"=="2" (
    echo.
    echo Starting with main parking environment...
    echo.
    C:\Users\Danix\anaconda3\Scripts\conda.exe run -n parking python run_server.py
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

pause
