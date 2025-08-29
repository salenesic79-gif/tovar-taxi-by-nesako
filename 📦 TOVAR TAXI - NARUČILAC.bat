@echo off
chcp 65001 >nul
title 📦 TOVAR TAXI - Naručilac transporta

echo.
echo ===============================================
echo    📦 TOVAR TAXI - NARUČILAC TRANSPORTA
echo ===============================================
echo.
echo 🔄 Pokretanje Django servera...
start /min python manage.py runserver 0.0.0.0:8000

echo ⏳ Čekanje da se server pokrene...
timeout /t 3 /nobreak >nul

echo.
echo 🌐 Otvaranje stranice za naručilac transporta...
echo 📋 Pristupni podaci:
echo    👤 Korisničko ime: naruci
echo    🔑 Lozinka: pass123
echo.
echo 💡 Stranica će se otvoriti automatski u browser-u
echo ⚠️  Ne zatvarajte ovaj prozor dok koristite aplikaciju!
echo.

start http://localhost:8000/dashboard/

echo 🎯 Aplikacija je pokrenuta!
echo 📱 Dashboard za naručilac transporta je otvoren
echo.
pause
