@echo off
chcp 65001 >nul
title 🚛 TOVAR TAXI - Prevoznik

echo.
echo ===============================================
echo    🚛 TOVAR TAXI - PREVOZNIK
echo ===============================================
echo.
echo 🔄 Pokretanje Django servera...
start /min python manage.py runserver 0.0.0.0:8000

echo ⏳ Čekanje da se server pokrene...
timeout /t 3 /nobreak >nul

echo.
echo 🌐 Otvaranje stranice za prevoznik...
echo 📋 Pristupni podaci:
echo    👤 Korisničko ime: prevoz
echo    🔑 Lozinka: pass123
echo.
echo 💡 Stranica će se otvoriti automatski u browser-u
echo ⚠️  Ne zatvarajte ovaj prozor dok koristite aplikaciju!
echo.

start http://localhost:8000/carrier-dashboard/

echo 🎯 Aplikacija je pokrenuta!
echo 🚛 Dashboard za prevoznik je otvoren
echo.
pause
