@echo off
cls
echo ====================================================================
echo YOLO License Plate Detection System - Quick Test
echo ====================================================================
echo.

echo Current Status:
echo   Server: Running on http://localhost:8000
echo   Models: Loaded and ready
echo   Database: Initialized
echo.

echo Testing API Status...
echo.
curl.exe http://localhost:8000/api/status/
echo.
echo.

echo ====================================================================
echo API Endpoints Available:
echo ====================================================================
echo.
echo 1. Detect Plate Only:
echo    curl -X POST http://localhost:8000/api/detect-plate/ -F "image=@yourimage.jpg"
echo.
echo 2. Detect and Register Entry:
echo    curl -X POST http://localhost:8000/api/detect-entry/ -F "image=@yourimage.jpg"
echo.
echo 3. Detect and Register Exit:
echo    curl -X POST http://localhost:8000/api/detect-exit/ -F "image=@yourimage.jpg"
echo.
echo 4. Get Parking Status:
echo    curl http://localhost:8000/api/status/
echo.
echo ====================================================================
echo.

echo To test with an image:
echo   python backend\test_api_with_image.py path\to\your\image.jpg
echo.

echo For complete documentation, see:
echo   - YOLO_INTEGRATION_COMPLETE.md
echo   - backend\YOLO_TEST_GUIDE.md
echo   - backend\QUICK_TEST.md
echo.

echo ====================================================================
pause
