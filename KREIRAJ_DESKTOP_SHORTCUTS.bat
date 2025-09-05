@echo off
cd /d "C:\Users\PC\Desktop\tovar-taxi-by-nesako"

echo Kreiranje desktop shortcut-ova...
echo.

REM Kreiranje VBS script-a za shortcut-ove
echo Set WshShell = CreateObject("WScript.Shell") > create_shortcuts.vbs
echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\T.TAXI.lnk") >> create_shortcuts.vbs
echo Shortcut.TargetPath = "%CD%\JEDNOSTAVAN_TEST.bat" >> create_shortcuts.vbs
echo Shortcut.WorkingDirectory = "%CD%" >> create_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi_icon.png" >> create_shortcuts.vbs
echo Shortcut.Description = "Pokrece TOVAR TAXI aplikaciju" >> create_shortcuts.vbs
echo Shortcut.Save >> create_shortcuts.vbs
echo. >> create_shortcuts.vbs

echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Naručilac.lnk") >> create_shortcuts.vbs
echo Shortcut.TargetPath = "http://localhost:8000/shipper-dashboard/" >> create_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi_icon.png" >> create_shortcuts.vbs
echo Shortcut.Description = "Kontrolna tabla za narucioce transporta" >> create_shortcuts.vbs
echo Shortcut.Save >> create_shortcuts.vbs
echo. >> create_shortcuts.vbs

echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk") >> create_shortcuts.vbs
echo Shortcut.TargetPath = "http://localhost:8000/carrier-dashboard/" >> create_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi_icon.png" >> create_shortcuts.vbs
echo Shortcut.Description = "Kontrolna tabla za prevoznike" >> create_shortcuts.vbs
echo Shortcut.Save >> create_shortcuts.vbs
echo. >> create_shortcuts.vbs

echo Set Shortcut = WshShell.CreateShortcut("%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk") >> create_shortcuts.vbs
echo Shortcut.TargetPath = "http://localhost:8000/admin/" >> create_shortcuts.vbs
echo Shortcut.IconLocation = "%CD%\static\images\TTaxi_icon.png" >> create_shortcuts.vbs
echo Shortcut.Description = "Administratorski panel" >> create_shortcuts.vbs
echo Shortcut.Save >> create_shortcuts.vbs

REM Pokretanje VBS script-a
cscript create_shortcuts.vbs

REM Brisanje privremenog VBS fajla
del create_shortcuts.vbs

echo.
echo Desktop shortcut-ovi uspesno kreirani:
echo T.TAXI
echo TOVAR TAXI Naručilac
echo TOVAR TAXI Prevoznik
echo TOVAR TAXI Admin
echo.
echo Svi shortcut-ovi imaju TTaxi_icon.png ikonu!
pause
