@echo off
REM Activate the backend virtual environment

echo Activating backend virtual environment...
call C:\Users\Danix\anaconda3\Scripts\activate.bat backend\venv

echo.
echo Virtual environment activated!
echo Python version:
python --version
echo.
echo You can now run:
echo   - python backend/src/yolo_loader.py
echo   - python backend/src/init_database.py
echo   - python run_server.py
echo.
