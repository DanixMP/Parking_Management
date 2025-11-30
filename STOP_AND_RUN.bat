@echo off
echo ====================================================================
echo Stopping old app and starting fresh...
echo ====================================================================
echo.

echo Killing any running parking.exe...
taskkill /F /IM parking.exe 2>nul
echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul
echo.

cd frontend\parking

echo Starting app...
echo.
echo GRANT CAMERA PERMISSION when Windows asks!
echo.

flutter run -d windows

pause
