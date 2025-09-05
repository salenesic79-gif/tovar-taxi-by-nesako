@echo off
title JEDNOSTAVAN PRISTUP - Desktop Shortcuts

echo.
echo ===============================================
echo    JEDNOSTAVAN PRISTUP - DESKTOP SHORTCUTS
echo ===============================================
echo.

echo Brisanje starih shortcuts...
del "%USERPROFILE%\Desktop\T.TAXI.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Narucilac.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk" 2>nul

echo.
echo Kreiranje URL shortcuts direktno...

echo [InternetShortcut] > "%USERPROFILE%\Desktop\T.TAXI - Pocetna.url"
echo URL=http://localhost:8000/ >> "%USERPROFILE%\Desktop\T.TAXI - Pocetna.url"
echo IconFile=%~dp0static\images\TTaxi.ico >> "%USERPROFILE%\Desktop\T.TAXI - Pocetna.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\T.TAXI - Pocetna.url"

echo [InternetShortcut] > "%USERPROFILE%\Desktop\TOVAR TAXI - Admin.url"
echo URL=http://localhost:8000/admin/ >> "%USERPROFILE%\Desktop\TOVAR TAXI - Admin.url"
echo IconFile=%~dp0static\images\TTaxi.ico >> "%USERPROFILE%\Desktop\TOVAR TAXI - Admin.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\TOVAR TAXI - Admin.url"

echo [InternetShortcut] > "%USERPROFILE%\Desktop\TOVAR TAXI - Signup.url"
echo URL=http://localhost:8000/signup/ >> "%USERPROFILE%\Desktop\TOVAR TAXI - Signup.url"
echo IconFile=%~dp0static\images\TTaxi.ico >> "%USERPROFILE%\Desktop\TOVAR TAXI - Signup.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\TOVAR TAXI - Signup.url"

echo.
echo Kreiranje BAT fajla za pokretanje servera...
echo @echo off > "%USERPROFILE%\Desktop\POKRENI SERVER.bat"
echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\POKRENI SERVER.bat"
echo title TOVAR TAXI - Server >> "%USERPROFILE%\Desktop\POKRENI SERVER.bat"
echo echo Pokretanje Django servera... >> "%USERPROFILE%\Desktop\POKRENI SERVER.bat"
echo python manage.py runserver 0.0.0.0:8000 >> "%USERPROFILE%\Desktop\POKRENI SERVER.bat"

echo.
echo ===============================================
echo    SHORTCUTS USPESNO KREIRANI!
echo ===============================================
echo.
echo KREIRANI SHORTCUTS:
echo   POKRENI SERVER.bat - Pokrece Django server
echo   T.TAXI - Pocetna.url - Glavna stranica
echo   TOVAR TAXI - Admin.url - Admin panel
echo   TOVAR TAXI - Signup.url - Registracija
echo.
echo KAKO KORISTITI:
echo 1. Pokreni "POKRENI SERVER.bat" PRVO
echo 2. Zatim koristi URL shortcuts
echo.
echo PRISTUPNI PODACI:
echo Admin: admin / admin123
echo.
pause
