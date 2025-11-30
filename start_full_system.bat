@echo off
echo ========================================
echo   Parking Management System Launcher
echo ========================================
echo.
echo Starting Django Backend Server...
start "Django Backend" cmd /k "cd backend && DjangoEnv\Scripts\activate && python manage.py runserver 8000"
echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul
echo.
echo Starting Flutter Frontend...
start "Flutter Frontend" cmd /k "cd frontend\parking && flutter run -d windows"
echo.
echo ========================================
echo Both servers are starting...
echo Django Backend: http://localhost:8000
echo Flutter Frontend: Will open automatically
echo ========================================
echo.
echo Press any key to exit this launcher window...
pause >nul
