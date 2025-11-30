@echo off
cls
echo ====================================================================
echo Rebuilding Flutter App with Camera Support
echo ====================================================================
echo.

cd frontend\parking

echo Step 1: Cleaning build...
call flutter clean

echo.
echo Step 2: Getting dependencies...
call flutter pub get

echo.
echo Step 3: Running app...
echo.
echo IMPORTANT: Grant camera permission when Windows asks!
echo.

call flutter run -d windows

pause
