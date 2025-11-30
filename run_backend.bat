@echo off
REM Run the parking backend application with conda environment

cd /d "%~dp0"

echo Starting Parking Management System Backend...
echo Environment: parking (Python 3.10.19)
echo.

C:\Users\Danix\anaconda3\Scripts\conda.exe run -n parking python backend/src/gui_qt.py

pause
