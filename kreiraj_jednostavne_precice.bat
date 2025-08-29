@echo off
title TOVAR TAXI - KREIRANJE PRECICA
color 0A

echo.
echo ========================================
echo    TOVAR TAXI - KREIRANJE PRECICA
echo ========================================
echo.

echo Brisanje starih precica...

REM Obriši sve stare Tovar Taxi prečice sa Desktop-a
del /f /q "C:\Users\PC\Desktop\TOVAR TAXI*.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\*TOVAR TAXI*.lnk" 2>nul

echo Stare precice obrisane!

echo.
echo Kreiranje novih funkcionalnih precica...

REM Kreiraj glavnu prečicu
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateMainShortcut.vbs"
echo sLinkFile = "C:\Users\PC\Desktop\TOVAR TAXI - POCETNA.lnk" >> "%temp%\CreateMainShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateMainShortcut.vbs"
echo oLink.TargetPath = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\FINALNI_POKRETANJE.bat" >> "%temp%\CreateMainShortcut.vbs"
echo oLink.WorkingDirectory = "C:\Users\PC\Desktop\tovar-taxi-by-nesako" >> "%temp%\CreateMainShortcut.vbs"
echo oLink.Description = "Pokreni Tovar Taxi aplikaciju" >> "%temp%\CreateMainShortcut.vbs"
echo oLink.IconLocation = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\static\images\TTaxi.ico,0" >> "%temp%\CreateMainShortcut.vbs"
echo oLink.Save >> "%temp%\CreateMainShortcut.vbs"

cscript //nologo "%temp%\CreateMainShortcut.vbs"

REM Kreiraj Admin prečicu
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateAdminShortcut.vbs"
echo sLinkFile = "C:\Users\PC\Desktop\TOVAR TAXI - ADMIN.lnk" >> "%temp%\CreateAdminShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.Arguments = "/k ""cd /d C:\Users\PC\Desktop\tovar-taxi-by-nesako && python manage.py runserver 0.0.0.0:8000""" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.WorkingDirectory = "C:\Users\PC\Desktop\tovar-taxi-by-nesako" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.Description = "Tovar Taxi Admin Panel" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.IconLocation = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\static\images\TTaxi.ico,0" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.Save >> "%temp%\CreateAdminShortcut.vbs"

cscript //nologo "%temp%\CreateAdminShortcut.vbs"

echo.
echo NOVE PRECICE KREIRANE:
echo    TOVAR TAXI - POCETNA.lnk
echo    TOVAR TAXI - ADMIN.lnk
echo.
echo Sve precice koriste TTaxi.ico ikonu i pokretaju server!
echo.
pause
