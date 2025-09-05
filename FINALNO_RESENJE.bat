@echo off
title FINALNO RESENJE - Desktop Shortcuts

echo.
echo ===============================================
echo    FINALNO RESENJE - DESKTOP SHORTCUTS
echo ===============================================
echo.

echo Brisanje starih shortcuts...
del "%USERPROFILE%\Desktop\T.TAXI.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Narucilac.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk" 2>nul

echo.
echo Kreiranje VBS script-a za shortcuts...

echo Set WshShell = CreateObject("WScript.Shell") > temp_shortcut.vbs
echo. >> temp_shortcut.vbs
echo ' T.TAXI - Glavna aplikacija >> temp_shortcut.vbs
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\T.TAXI.lnk") >> temp_shortcut.vbs
echo Shortcut.TargetPath = "%~dp0POCETNA_SIMPLE.bat" >> temp_shortcut.vbs
echo Shortcut.WorkingDirectory = "%~dp0" >> temp_shortcut.vbs
echo Shortcut.Save >> temp_shortcut.vbs
echo. >> temp_shortcut.vbs
echo ' TOVAR TAXI Narucilac >> temp_shortcut.vbs
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Narucilac.lnk") >> temp_shortcut.vbs
echo Shortcut.TargetPath = "cmd.exe" >> temp_shortcut.vbs
echo Shortcut.Arguments = "/c start http://localhost:8000/shipper-dashboard/" >> temp_shortcut.vbs
echo Shortcut.Save >> temp_shortcut.vbs
echo. >> temp_shortcut.vbs
echo ' TOVAR TAXI Prevoznik >> temp_shortcut.vbs
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk") >> temp_shortcut.vbs
echo Shortcut.TargetPath = "cmd.exe" >> temp_shortcut.vbs
echo Shortcut.Arguments = "/c start http://localhost:8000/carrier-dashboard/" >> temp_shortcut.vbs
echo Shortcut.Save >> temp_shortcut.vbs
echo. >> temp_shortcut.vbs
echo ' TOVAR TAXI Admin >> temp_shortcut.vbs
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk") >> temp_shortcut.vbs
echo Shortcut.TargetPath = "cmd.exe" >> temp_shortcut.vbs
echo Shortcut.Arguments = "/c start http://localhost:8000/admin/" >> temp_shortcut.vbs
echo Shortcut.Save >> temp_shortcut.vbs

echo Pokretanje VBS script-a...
cscript //nologo temp_shortcut.vbs

echo Brisanje privremenog fajla...
del temp_shortcut.vbs

echo.
echo ===============================================
echo    SHORTCUTS USPESNO KREIRANI!
echo ===============================================
echo.
echo KREIRANI SHORTCUTS:
echo   T.TAXI - Pokrece aplikaciju i server
echo   TOVAR TAXI Narucilac - Otvara shipper-dashboard
echo   TOVAR TAXI Prevoznik - Otvara carrier-dashboard  
echo   TOVAR TAXI Admin - Otvara admin panel
echo.
echo KAKO KORISTITI:
echo 1. Pokreni T.TAXI da pokrenes server
echo 2. Zatim koristi ostale shortcuts za pristup
echo.
echo PRISTUPNI PODACI:
echo Admin: admin / admin123
echo Narucilac: naruci / pass123
echo Prevoznik: prevoz / pass123
echo.
pause
