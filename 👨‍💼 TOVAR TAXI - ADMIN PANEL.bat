@echo off
chcp 65001 >nul
title 👨‍💼 TOVAR TAXI - Admin panel

echo.
echo ===============================================
echo    👨‍💼 TOVAR TAXI - ADMIN PANEL
echo ===============================================
echo.
echo 🔄 Pokretanje Django servera...
start /min python manage.py runserver 0.0.0.0:8000

echo ⏳ Čekanje da se server pokrene...
timeout /t 3 /nobreak >nul

echo.
echo 🌐 Otvaranje admin panela...
echo 📋 Pristupni podaci:
echo    👤 Korisničko ime: admin
echo    🔑 Lozinka: admin123
echo.
echo 💡 Admin panel će se otvoriti automatski u browser-u
echo ⚠️  Ne zatvarajte ovaj prozor dok koristite aplikaciju!
echo.

start http://localhost:8000/admin/

echo 🎯 Aplikacija je pokrenuta!
echo 👨‍💼 Admin panel je otvoren
echo.
pause
