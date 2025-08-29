@echo off
title TOVAR TAXI - Početna stranica
color 0A
echo.
echo ===============================================
echo    🚀 TOVAR TAXI - POČETNA STRANICA
echo ===============================================
echo.
echo Pokretanje Django servera...
echo Aplikacija će biti dostupna na:
echo.
echo 💻 Lokalno: http://localhost:8000
echo 🌐 Mreža:   http://[VAŠA_IP]:8000
echo.
echo ⚡ Čeka se pokretanje servera...
echo.

cd /d "%~dp0"
python manage.py runserver 0.0.0.0:8000

pause
