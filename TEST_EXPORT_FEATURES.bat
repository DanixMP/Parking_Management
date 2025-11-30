@echo off
echo ========================================
echo   Export & Shamsi Date Testing
echo ========================================
echo.

cd frontend\parking

echo [1/3] Installing dependencies...
call flutter pub get
if errorlevel 1 (
    echo ERROR: Failed to get dependencies
    pause
    exit /b 1
)
echo.

echo [2/3] Running Flutter analyze...
call flutter analyze --no-fatal-infos
echo.

echo [3/3] Starting Flutter app...
echo.
echo Navigate to Reports screen to test export features
echo.
call flutter run

pause
