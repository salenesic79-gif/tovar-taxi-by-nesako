@echo off
title TOVAR TAXI - LEPO VIDLJIVI SHORTCUTS

echo.
echo ===============================================
echo    KREIRANJE LEPO VIDLJIVIH SHORTCUTS
echo ===============================================
echo.

echo Brisanje APSOLUTNO SVIH shortcuts i fajlova...
del "%USERPROFILE%\Desktop\*.url" 2>nul
del "%USERPROFILE%\Desktop\*.lnk" 2>nul
del "%USERPROFILE%\Desktop\*.cmd" 2>nul
del "%USERPROFILE%\Desktop\T.TAXI*" 2>nul
del "%USERPROFILE%\Desktop\TOVAR*" 2>nul
del "%USERPROFILE%\Desktop\ADMIN*" 2>nul
del "%USERPROFILE%\Desktop\NARUCILAC*" 2>nul
del "%USERPROFILE%\Desktop\PREVOZNIK*" 2>nul
del "%USERPROFILE%\Desktop\POCETNA*" 2>nul
del "%USERPROFILE%\Desktop\TTaxi*" 2>nul

echo.
echo Konvertovanje PNG u ICO za bolje ikone...
python convert_ttaxi_icon.py

echo.
echo Kreiranje PowerShell shortcuts sa ICO ikonama...

echo [InternetShortcut] > "%USERPROFILE%\Desktop\🚀 TOVAR TAXI - Početna.url"
echo URL=file:///%CD%/POCETNA_SIMPLE.bat >> "%USERPROFILE%\Desktop\🚀 TOVAR TAXI - Početna.url"
echo IconFile=%CD%\static\images\TTaxi_icon.ico.ico >> "%USERPROFILE%\Desktop\🚀 TOVAR TAXI - Početna.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\🚀 TOVAR TAXI - Početna.url"

echo [InternetShortcut] > "%USERPROFILE%\Desktop\📦 TOVAR TAXI - Naručilac.url"
echo URL=file:///%CD%/NARUCILAC_SIMPLE.bat >> "%USERPROFILE%\Desktop\📦 TOVAR TAXI - Naručilac.url"
echo IconFile=%CD%\static\images\TTaxi_icon.ico.ico >> "%USERPROFILE%\Desktop\📦 TOVAR TAXI - Naručilac.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\📦 TOVAR TAXI - Naručilac.url"

echo [InternetShortcut] > "%USERPROFILE%\Desktop\🚛 TOVAR TAXI - Prevoznik.url"
echo URL=file:///%CD%/PREVOZNIK_SIMPLE.bat >> "%USERPROFILE%\Desktop\🚛 TOVAR TAXI - Prevoznik.url"
echo IconFile=%CD%\static\images\TTaxi_icon.ico.ico >> "%USERPROFILE%\Desktop\🚛 TOVAR TAXI - Prevoznik.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\🚛 TOVAR TAXI - Prevoznik.url"

echo [InternetShortcut] > "%USERPROFILE%\Desktop\👨‍💼 TOVAR TAXI - Admin Panel.url"
echo URL=file:///%CD%/ADMIN_SIMPLE.bat >> "%USERPROFILE%\Desktop\👨‍💼 TOVAR TAXI - Admin Panel.url"
echo IconFile=%CD%\static\images\TTaxi_icon.ico.ico >> "%USERPROFILE%\Desktop\👨‍💼 TOVAR TAXI - Admin Panel.url"
echo IconIndex=0 >> "%USERPROFILE%\Desktop\👨‍💼 TOVAR TAXI - Admin Panel.url"

echo.
echo Kreiranje folder pristupa kao backup...
echo @echo off > "%USERPROFILE%\Desktop\📁 TOVAR TAXI - OTVORI FOLDER.bat"
echo title TOVAR TAXI - Otvori Folder >> "%USERPROFILE%\Desktop\📁 TOVAR TAXI - OTVORI FOLDER.bat"
echo explorer "%~dp0" >> "%USERPROFILE%\Desktop\📁 TOVAR TAXI - OTVORI FOLDER.bat"

echo.
echo ✅ LEPO VIDLJIVI SHORTCUTS KREIRANI:
echo    🚀 TOVAR TAXI - Početna.url (sa ikonom)
echo    👨‍💼 TOVAR TAXI - Admin Panel.url (sa ikonom)
echo    📦 TOVAR TAXI - Naručilac.url (sa ikonom)
echo    🚛 TOVAR TAXI - Prevoznik.url (sa ikonom)
echo    📁 TOVAR TAXI - OTVORI FOLDER.bat (backup)
echo.
echo 💡 Koristi ULTRA SHARP ICO ikone za maksimalnu jasnoću
echo 🎯 Emoji + nazivi za lako prepoznavanje
echo 🔥 PowerShell shortcuts sa pravim ikonama
echo.
pause
