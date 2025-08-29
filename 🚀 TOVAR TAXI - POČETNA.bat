@echo off
chcp 65001 >nul
title 🚀 TOVAR TAXI - Početna stranica

echo.
echo ===============================================
echo    🚀 TOVAR TAXI - POKRETANJE APLIKACIJE
echo ===============================================
echo.
echo 📋 Korak 1: Instaliranje zavisnosti...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Greška pri instaliranju zavisnosti!
    pause
    exit /b 1
)

echo.
echo 📋 Korak 2: Pokretanje migracija...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Greška pri migraciji baze podataka!
    pause
    exit /b 1
)

echo.
echo 📋 Korak 3: Kreiranje test korisnika...
python create_test_users.py
if errorlevel 1 (
    echo ❌ Greška pri kreiranju test korisnika!
    pause
    exit /b 1
)

echo.
echo 📋 Korak 4: Pokretanje Django servera...
echo.
echo 🌐 Server će biti dostupan na: http://localhost:8000/
echo.
echo 📋 PRISTUPNI PODACI:
echo 👨‍💼 Admin: admin / admin123
echo 📦 Naručilac: naruci / pass123  
echo 🚛 Prevoznik: prevoz / pass123
echo.
echo ⚠️  Ostavite ovaj prozor otvoren dok koristite aplikaciju!
echo 🔗 Otvorite browser i idite na: http://localhost:8000/
echo.

start http://localhost:8000/
python manage.py runserver 0.0.0.0:8000
