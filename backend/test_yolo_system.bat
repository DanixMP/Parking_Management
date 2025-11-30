@echo off
echo ====================================================================
echo YOLO Integration Test Suite
echo ====================================================================
echo.

echo Activating Django environment...
call DjangoEnv\Scripts\activate.bat

echo.
echo Running integration tests...
echo.
python test_yolo_integration.py

echo.
echo ====================================================================
echo Test complete!
echo.
echo Next steps:
echo 1. If tests passed, start Django server:
echo    python manage.py runserver 8000
echo.
echo 2. Test with images:
echo    python test_api_with_image.py path\to\image.jpg
echo.
echo 3. See YOLO_TEST_GUIDE.md for detailed instructions
echo ====================================================================
echo.

pause
