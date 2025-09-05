@echo off
title TOVAR TAXI - INSTALL DEPENDENCIES
color 0B

echo.
echo ========================================
echo   TOVAR TAXI - INSTALLING DEPENDENCIES
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Installing required Python packages...
echo.

REM Install packages one by one to catch any errors
echo Installing Django...
pip install Django==4.2.7

echo Installing channels...
pip install channels==4.0.0

echo Installing channels-redis...
pip install channels-redis==4.1.0

echo Installing redis...
pip install redis==5.0.1

echo Installing python-decouple...
pip install python-decouple==3.8

echo Installing whitenoise...
pip install whitenoise==6.6.0

echo Installing gunicorn...
pip install gunicorn==21.2.0

echo Installing stripe...
pip install stripe==7.8.0

echo Installing geopy...
pip install geopy==2.4.1

echo Installing requests (for ngrok test mode)...
pip install requests

echo.
echo ========================================
echo   DEPENDENCIES INSTALLATION COMPLETE
echo ========================================
echo.

echo Running Django migrations...
python manage.py migrate

echo.
echo All dependencies installed successfully!
echo You can now run: python manage.py runserver
echo.
pause
