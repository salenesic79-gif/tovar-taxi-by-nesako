@echo off
title TOVAR TAXI - Naručilac transporta
color 0E
echo.
echo ===============================================
echo    📦 TOVAR TAXI - NARUČILAC TRANSPORTA
echo ===============================================
echo.
echo Pokretanje aplikacije za naručioce...
echo.
echo 📋 Dashboard:        http://localhost:8000/
echo 📦 Pošalji teret:    http://localhost:8000/create-shipment/
echo 🚛 Freight Exchange: http://localhost:8000/freight-exchange/
echo 💬 Moje ture:        http://localhost:8000/ture/
echo ⚙️  Podešavanja:     http://localhost:8000/settings/
echo.
echo 🌐 Pristup sa drugih uređaja: http://[VAŠA_IP]:8000
echo.
echo 👤 Test nalog - Korisničko ime: narucilac
echo 🔑 Lozinka: test123
echo.

cd /d "%~dp0"
start "" "http://localhost:8000/"
python manage.py runserver 0.0.0.0:8000

pause
