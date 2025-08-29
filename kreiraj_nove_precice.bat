@echo off
title TOVAR TAXI - KREIRANJE NOVIH PREČICA
color 0A

echo.
echo ========================================
echo    🚛 TOVAR TAXI - KREIRANJE PREČICA
echo ========================================
echo.

echo 🗑️ Brisanje starih prečica...

REM Obriši sve stare Tovar Taxi prečice sa Desktop-a
del /f /q "C:\Users\PC\Desktop\TOVAR TAXI - ADMIN PANEL.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\TOVAR TAXI - ADMIN.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\TOVAR TAXI - NARUČILAC.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\TOVAR TAXI - POČETNA.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\TOVAR TAXI - PREVOZNIK.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\NARUČILAC TRANSPORTA.lnk" 2>nul
del /f /q "C:\Users\PC\Desktop\PREVOZNIK (VOZAČ).lnk" 2>nul

echo ✅ Stare prečice obrisane!

echo.
echo 🔧 Kreiranje novih funkcionalnih prečica...

REM Kreiraj VBS script za prečice
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShortcut.vbs"
echo sLinkFile = "C:\Users\PC\Desktop\🚀 TOVAR TAXI - POČETNA.lnk" >> "%temp%\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShortcut.vbs"
echo oLink.TargetPath = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\FINALNI_POKRETANJE.bat" >> "%temp%\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "C:\Users\PC\Desktop\tovar-taxi-by-nesako" >> "%temp%\CreateShortcut.vbs"
echo oLink.Description = "Pokreni Tovar Taxi aplikaciju" >> "%temp%\CreateShortcut.vbs"
echo oLink.IconLocation = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\static\images\TTaxi.ico,0" >> "%temp%\CreateShortcut.vbs"
echo oLink.Save >> "%temp%\CreateShortcut.vbs"

REM Pokreni VBS script
cscript //nologo "%temp%\CreateShortcut.vbs"

REM Kreiraj Admin prečicu
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateAdminShortcut.vbs"
echo sLinkFile = "C:\Users\PC\Desktop\👨‍💼 TOVAR TAXI - ADMIN.lnk" >> "%temp%\CreateAdminShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.Arguments = "/c ""cd /d C:\Users\PC\Desktop\tovar-taxi-by-nesako && python manage.py runserver 0.0.0.0:8000 && timeout 3 && start http://localhost:8000/admin/""" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.WorkingDirectory = "C:\Users\PC\Desktop\tovar-taxi-by-nesako" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.Description = "Tovar Taxi Admin Panel" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.IconLocation = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\static\images\TTaxi.ico,0" >> "%temp%\CreateAdminShortcut.vbs"
echo oLink.Save >> "%temp%\CreateAdminShortcut.vbs"

cscript //nologo "%temp%\CreateAdminShortcut.vbs"

REM Kreiraj Naručilac prečicu
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateShipperShortcut.vbs"
echo sLinkFile = "C:\Users\PC\Desktop\📦 TOVAR TAXI - NARUČILAC.lnk" >> "%temp%\CreateShipperShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateShipperShortcut.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%temp%\CreateShipperShortcut.vbs"
echo oLink.Arguments = "/c ""cd /d C:\Users\PC\Desktop\tovar-taxi-by-nesako && python manage.py runserver 0.0.0.0:8000 && timeout 3 && start http://localhost:8000/shipper-dashboard/""" >> "%temp%\CreateShipperShortcut.vbs"
echo oLink.WorkingDirectory = "C:\Users\PC\Desktop\tovar-taxi-by-nesako" >> "%temp%\CreateShipperShortcut.vbs"
echo oLink.Description = "Tovar Taxi Naručilac Dashboard" >> "%temp%\CreateShipperShortcut.vbs"
echo oLink.IconLocation = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\static\images\TTaxi.ico,0" >> "%temp%\CreateShipperShortcut.vbs"
echo oLink.Save >> "%temp%\CreateShipperShortcut.vbs"

cscript //nologo "%temp%\CreateShipperShortcut.vbs"

REM Kreiraj Prevoznik prečicu
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\CreateCarrierShortcut.vbs"
echo sLinkFile = "C:\Users\PC\Desktop\🚛 TOVAR TAXI - PREVOZNIK.lnk" >> "%temp%\CreateCarrierShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\CreateCarrierShortcut.vbs"
echo oLink.TargetPath = "cmd.exe" >> "%temp%\CreateCarrierShortcut.vbs"
echo oLink.Arguments = "/c ""cd /d C:\Users\PC\Desktop\tovar-taxi-by-nesako && python manage.py runserver 0.0.0.0:8000 && timeout 3 && start http://localhost:8000/carrier-dashboard/""" >> "%temp%\CreateCarrierShortcut.vbs"
echo oLink.WorkingDirectory = "C:\Users\PC\Desktop\tovar-taxi-by-nesako" >> "%temp%\CreateCarrierShortcut.vbs"
echo oLink.Description = "Tovar Taxi Prevoznik Dashboard" >> "%temp%\CreateCarrierShortcut.vbs"
echo oLink.IconLocation = "C:\Users\PC\Desktop\tovar-taxi-by-nesako\static\images\TTaxi.ico,0" >> "%temp%\CreateCarrierShortcut.vbs"
echo oLink.Save >> "%temp%\CreateCarrierShortcut.vbs"

cscript //nologo "%temp%\CreateCarrierShortcut.vbs"

REM Obriši temp fajlove
del "%temp%\CreateShortcut.vbs" 2>nul
del "%temp%\CreateAdminShortcut.vbs" 2>nul
del "%temp%\CreateShipperShortcut.vbs" 2>nul
del "%temp%\CreateCarrierShortcut.vbs" 2>nul

echo.
echo ✅ NOVE PREČICE KREIRANE:
echo    🚀 TOVAR TAXI - POČETNA.lnk
echo    👨‍💼 TOVAR TAXI - ADMIN.lnk
echo    📦 TOVAR TAXI - NARUČILAC.lnk
echo    🚛 TOVAR TAXI - PREVOZNIK.lnk
echo.
echo 💡 Sve prečice koriste TTaxi.ico ikonu i pokretaju server automatski!
echo.
pause
