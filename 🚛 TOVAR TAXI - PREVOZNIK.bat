@echo off
title TOVAR TAXI - Prevoznik
color 0D
echo.
echo ===============================================
echo    🚛 TOVAR TAXI - PREVOZNIK (VOZAČ)
echo ===============================================
echo.
echo Pokretanje aplikacije za prevoznike...
echo.
echo 🏠 Dashboard:        http://localhost:8000/
echo 🚛 Moja vozila:      http://localhost:8000/vehicles/
echo 📋 Moje ture:        http://localhost:8000/ture/
echo 💬 Chat sistem:      http://localhost:8000/ture/
echo 🔔 Notifikacije:     http://localhost:8000/notifikacije/
echo ⚙️  Podešavanja:     http://localhost:8000/settings/
echo.
echo 🌐 Pristup sa drugih uređaja: http://[VAŠA_IP]:8000
echo.
echo 👤 Test nalog - Korisničko ime: prevoznik
echo 🔑 Lozinka: test123
echo.

cd /d "%~dp0"
start "" "http://localhost:8000/"
python manage.py runserver 0.0.0.0:8000

pause
