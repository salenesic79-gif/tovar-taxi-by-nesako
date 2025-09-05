@echo off
title TOVAR TAXI - Prevoznik

echo.
echo ===============================================
echo    TOVAR TAXI - PREVOZNIK
echo ===============================================
echo.
echo Otvaranje stranice za prevoznik...
echo.
echo Pristupni podaci:
echo    Korisnicko ime: prevoz
echo    Lozinka: pass123
echo.
echo Stranica ce se otvoriti automatski u browser-u
echo.

start http://localhost:8000/carrier-dashboard/

echo Dashboard za prevoznik je otvoren
echo.
pause
