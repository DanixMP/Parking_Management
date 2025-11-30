@echo off
cls
echo ====================================================================
echo Rebuilding Flutter App - Fixing Lock Issue
echo ====================================================================
echo.

echo Step 1: Stopping any running Flutter processes...
taskkill /F /IM parking.exe 2>nul
taskkill /F /IM flutter.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Cleaning build directory...
cd frontend\parking
rmdir /s /q build 2>nul
timeout /t 1 /nobreak >nul

echo.
echo Step 3: Flutter clean...
call flutter clean

echo.
echo Step 4: Getting dependencies...
call flutter pub get

echo.
echo Step 5: Building and running...
echo.
echo IMPORTANT: When Windows asks for camera permission, click ALLOW!
echo.
timeout /t 2 /nobreak

call flutter run -d windows

pause
