@echo off
cd /d "C:\Users\PC\Desktop\tovar-taxi-by-nesako"

echo ========================================
echo    KREIRANJE NOVIH TOVAR TAXI SHORTCUTS
echo    (ALTERNATIVNA METODA - POWERSHELL)
echo ========================================
echo.

REM Kreiranje PowerShell script-a za shortcut-ove
echo $WshShell = New-Object -ComObject WScript.Shell > create_shortcuts.ps1

REM 1. T.TAXI - Glavna aplikacija
echo $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\T.TAXI.lnk") >> create_shortcuts.ps1
echo $Shortcut.TargetPath = "%CD%\JEDNOSTAVAN_TEST.bat" >> create_shortcuts.ps1
echo $Shortcut.WorkingDirectory = "%CD%" >> create_shortcuts.ps1
echo $Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico,0" >> create_shortcuts.ps1
echo $Shortcut.Description = "Pokrece TOVAR TAXI aplikaciju" >> create_shortcuts.ps1
echo $Shortcut.Save() >> create_shortcuts.ps1
echo. >> create_shortcuts.ps1

REM 2. TOVAR TAXI Naručilac - Shipper dashboard  
echo $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\TOVAR TAXI Naručilac.lnk") >> create_shortcuts.ps1
echo $Shortcut.TargetPath = "C:\Windows\System32\cmd.exe" >> create_shortcuts.ps1
echo $Shortcut.Arguments = "/c start http://localhost:8000/shipper-dashboard/" >> create_shortcuts.ps1
echo $Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico,0" >> create_shortcuts.ps1
echo $Shortcut.Description = "Kontrolna tabla za narucioce transporta" >> create_shortcuts.ps1
echo $Shortcut.Save() >> create_shortcuts.ps1
echo. >> create_shortcuts.ps1

REM 3. TOVAR TAXI Prevoznik - Carrier dashboard
echo $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\TOVAR TAXI Prevoznik.lnk") >> create_shortcuts.ps1
echo $Shortcut.TargetPath = "C:\Windows\System32\cmd.exe" >> create_shortcuts.ps1
echo $Shortcut.Arguments = "/c start http://localhost:8000/carrier-dashboard/" >> create_shortcuts.ps1
echo $Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico,0" >> create_shortcuts.ps1
echo $Shortcut.Description = "Kontrolna tabla za prevoznike" >> create_shortcuts.ps1
echo $Shortcut.Save() >> create_shortcuts.ps1
echo. >> create_shortcuts.ps1

REM 4. TOVAR TAXI Admin - Admin panel
echo $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\TOVAR TAXI Admin.lnk") >> create_shortcuts.ps1
echo $Shortcut.TargetPath = "C:\Windows\System32\cmd.exe" >> create_shortcuts.ps1
echo $Shortcut.Arguments = "/c start http://localhost:8000/admin/" >> create_shortcuts.ps1
echo $Shortcut.IconLocation = "%CD%\static\images\TTaxi.ico,0" >> create_shortcuts.ps1
echo $Shortcut.Description = "Administratorski panel" >> create_shortcuts.ps1
echo $Shortcut.Save() >> create_shortcuts.ps1

echo Pokretanje PowerShell script-a...
powershell -ExecutionPolicy Bypass -File create_shortcuts.ps1

echo Brisanje privremenog PowerShell fajla...
del create_shortcuts.ps1

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
echo Svi shortcut-ovi koriste TTaxi.ico ikonu sa ,0 indeksom!
echo.
pause
