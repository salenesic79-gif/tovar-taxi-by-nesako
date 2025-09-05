@echo off
title TOVAR TAXI - Admin panel

echo.
echo ===============================================
echo    TOVAR TAXI - ADMIN PANEL
echo ===============================================
echo.
echo Otvaranje admin panela...
echo.
echo Pristupni podaci:
echo    Korisnicko ime: admin
echo    Lozinka: admin123
echo.
echo Admin panel ce se otvoriti automatski u browser-u
echo.

start http://localhost:8000/admin/

echo Admin panel je otvoren
echo.
pause
