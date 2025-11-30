@echo off
echo ========================================
echo   سیستم مدیریت پارکینگ
echo   Parking Management System
echo ========================================
echo.
echo Starting Django Backend...
echo.

start "Django Backend" cmd /k "cd backend && DjangoEnv\Scripts\activate && python manage.py runserver 8000"

timeout /t 3 /nobreak > nul

echo.
echo Backend started on http://localhost:8000
echo.
echo Starting Flutter Frontend...
echo.

start "Flutter Frontend" cmd /k "cd frontend\parking && flutter run -d windows"

echo.
echo ========================================
echo   Both systems are starting...
echo   Django: http://localhost:8000
echo   Flutter: Will open automatically
echo ========================================
echo.
pause
