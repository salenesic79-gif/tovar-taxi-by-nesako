@echo off
title TOVAR TAXI - FINALNO POKRETANJE SERVERA
color 0A

echo.
echo ========================================
echo    🚛 TOVAR TAXI - FINALNO POKRETANJE
echo ========================================
echo.

cd /d "c:\Users\PC\Desktop\tovar-taxi-by-nesako"

echo 🔧 Pokretam Django server na 0.0.0.0:8000...
echo.

REM Pokretanje servera u background procesu
start /B python manage.py runserver 0.0.0.0:8000

echo ⏳ Čekam da se server pokrene...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 PRISTUP SA DRUGIH UREĐAJA:
echo    http://192.168.0.21:8000
echo.
echo 📱 TEST NALOZI:
echo    👤 Admin: admin / admin123
echo    📦 Naručilac: narucilac / test123  
echo    🚛 Prevoznik: prevoznik / test123
echo.
echo 🚀 Otvaranje glavne stranice...

REM Otvaranje browser-a sa glavnom stranicom
start http://localhost:8000

echo.
echo ✅ SERVER JE POKRENNUT!
echo 💡 Ostavite ovaj prozor otvoren dok koristite aplikaciju
echo.
pause
