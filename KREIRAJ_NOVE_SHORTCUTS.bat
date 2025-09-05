@echo off
cd /d "C:\Users\PC\Desktop\tovar-taxi-by-nesako"

echo ========================================
echo    KREIRANJE NOVIH TOVAR TAXI SHORTCUTS
echo ========================================
echo.

REM Kreiranje VBS script-a za shortcut-ove
echo Set WshShell = CreateObject("WScript.Shell") > create_new_shortcuts.vbs

REM 1. T.TAXI - Glavna aplikacija
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\T.TAXI.lnk") >> create_new_shortcuts.vbs
echo Shortcut.TargetPath = "%CD%\JEDNOSTAVAN_TEST.bat" >> create_new_shortcuts.vbs
echo Shortcut.WorkingDirectory = "%CD%" >> create_new_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico" >> create_new_shortcuts.vbs
echo Shortcut.Description = "Pokrece TOVAR TAXI aplikaciju" >> create_new_shortcuts.vbs
echo Shortcut.Save >> create_new_shortcuts.vbs
echo. >> create_new_shortcuts.vbs

REM 2. TOVAR TAXI Naručilac - Shipper dashboard
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Naručilac.lnk") >> create_new_shortcuts.vbs
echo Shortcut.TargetPath = "http://localhost:8000/shipper-dashboard/" >> create_new_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico" >> create_new_shortcuts.vbs
echo Shortcut.Description = "Kontrolna tabla za narucioce transporta" >> create_new_shortcuts.vbs
echo Shortcut.Save >> create_new_shortcuts.vbs
echo. >> create_new_shortcuts.vbs

REM 3. TOVAR TAXI Prevoznik - Carrier dashboard
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk") >> create_new_shortcuts.vbs
echo Shortcut.TargetPath = "http://localhost:8000/carrier-dashboard/" >> create_new_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico" >> create_new_shortcuts.vbs
echo Shortcut.Description = "Kontrolna tabla za prevoznike" >> create_new_shortcuts.vbs
echo Shortcut.Save >> create_new_shortcuts.vbs
echo. >> create_new_shortcuts.vbs

REM 4. TOVAR TAXI Admin - Admin panel
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk") >> create_new_shortcuts.vbs
echo Shortcut.TargetPath = "http://localhost:8000/admin/" >> create_new_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico" >> create_new_shortcuts.vbs
echo Shortcut.Description = "Administratorski panel" >> create_new_shortcuts.vbs
echo Shortcut.Save >> create_new_shortcuts.vbs

echo Pokretanje VBS script-a...
cscript create_new_shortcuts.vbs

echo Brisanje privremenog VBS fajla...
del create_new_shortcuts.vbs

echo.
echo ========================================
echo   USPEŠNO KREIRANI NOVI SHORTCUTS!
echo ========================================
echo.
echo Desktop shortcut-ovi:
echo [1] T.TAXI (glavna aplikacija)
echo [2] TOVAR TAXI Naručilac (shipper dashboard)
echo [3] TOVAR TAXI Prevoznik (carrier dashboard)
echo [4] TOVAR TAXI Admin (admin panel)
echo.
echo Svi shortcut-ovi koriste TTaxi.ico ikonu!
echo.
pause
