@echo off
title TOVAR TAXI - Admin Panel
color 0B
echo.
echo ===============================================
echo    👨‍💼 TOVAR TAXI - ADMIN PANEL
echo ===============================================
echo.
echo Pokretanje Django servera i otvaranje Admin panela...
echo.
echo 🔧 Admin panel: http://localhost:8000/admin/
echo 🌐 Mreža:       http://[VAŠA_IP]:8000/admin/
echo.
echo 👤 Korisničko ime: admin
echo 🔑 Lozinka: admin123
echo.

cd /d "%~dp0"
start "" "http://localhost:8000/admin/"
python manage.py runserver 0.0.0.0:8000

pause
