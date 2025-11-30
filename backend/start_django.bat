@echo off
echo ====================================================================
echo Starting Django API Server with YOLO Integration
echo ====================================================================
echo.

echo Activating Django environment...
call DjangoEnv\Scripts\activate.bat

echo.
echo Starting server on http://localhost:8000
echo.
echo Available endpoints:
echo   - POST /api/detect-plate/     (Detect plate only)
echo   - POST /api/detect-entry/     (Detect and register entry)
echo   - POST /api/detect-exit/      (Detect and register exit)
echo   - GET  /api/status/           (Get parking status)
echo.
echo Press Ctrl+C to stop the server
echo ====================================================================
echo.

python manage.py runserver 8000
