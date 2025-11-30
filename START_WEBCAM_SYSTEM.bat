@echo off
cls
echo ====================================================================
echo Starting Automatic Parking System with Webcam
echo ====================================================================
echo.

echo Step 1: Installing Flutter dependencies...
cd frontend\parking
call flutter pub get
echo.

echo Step 2: Checking Django server...
echo.
echo Please ensure Django server is running in another terminal:
echo    cd backend
echo    .\DjangoEnv\Scripts\python.exe manage.py runserver 8000
echo.

pause

echo Step 3: Starting Flutter app with webcam...
echo.
call flutter run -d windows

pause
