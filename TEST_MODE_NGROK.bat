@echo off
chcp 65001 >nul
cls

echo ========================================
echo    TOVAR TAXI - TEST MODE SETUP
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if ngrok is available
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Ngrok is not installed or not in PATH
    echo Please download ngrok from: https://ngrok.com/download
    echo Extract it and add to your PATH, or place ngrok.exe in this folder
    echo.
    echo Continuing without ngrok - local access only...
    echo.
    
    REM Run without ngrok
    echo Starting Django server (local access only)...
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
) else (
    REM Run with ngrok
    echo Starting test mode with ngrok...
    python test_mode_ngrok.py
)

pause
