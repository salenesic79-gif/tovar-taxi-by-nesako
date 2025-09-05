@echo off
title TOVAR TAXI - Narucilac transporta

echo.
echo ===============================================
echo    TOVAR TAXI - NARUCILAC TRANSPORTA
echo ===============================================
echo.
echo Otvaranje stranice za narucilac transporta...
echo.
echo Pristupni podaci:
echo    Korisnicko ime: naruci
echo    Lozinka: pass123
echo.
echo Stranica ce se otvoriti automatski u browser-u
echo.

start http://localhost:8000/dashboard/

echo Dashboard za narucilac transporta je otvoren
echo.
pause
