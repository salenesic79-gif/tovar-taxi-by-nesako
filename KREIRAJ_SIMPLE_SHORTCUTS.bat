@echo off
title Kreiranje Simple Desktop Shortcuts

echo.
echo ===============================================
echo    KREIRANJE SIMPLE DESKTOP SHORTCUTS
echo ===============================================
echo.

echo Brisanje starih shortcuts...
del "%USERPROFILE%\Desktop\T.TAXI.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Narucilac.lnk" 2>nul
del "%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk" 2>nul

echo Stari shortcuts obrisani

echo.
echo Kreiranje novih shortcuts sa PowerShell...

powershell -ExecutionPolicy Bypass -Command "
$WshShell = New-Object -comObject WScript.Shell;
$IconPath = '%~dp0static\images\TTaxi.png';

# T.TAXI - Glavna aplikacija
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\T.TAXI.lnk');
$Shortcut.TargetPath = '%~dp0POCETNA_SIMPLE.bat';
$Shortcut.WorkingDirectory = '%~dp0';
$Shortcut.IconLocation = $IconPath;
$Shortcut.Save();

# TOVAR TAXI Naručilac
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\TOVAR TAXI Naručilac.lnk');
$Shortcut.TargetPath = '%~dp0NARUCILAC_SIMPLE.bat';
$Shortcut.WorkingDirectory = '%~dp0';
$Shortcut.IconLocation = $IconPath;
$Shortcut.Save();

# TOVAR TAXI Prevoznik
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\TOVAR TAXI Prevoznik.lnk');
$Shortcut.TargetPath = '%~dp0PREVOZNIK_SIMPLE.bat';
$Shortcut.WorkingDirectory = '%~dp0';
$Shortcut.IconLocation = $IconPath;
$Shortcut.Save();

# TOVAR TAXI Admin
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\TOVAR TAXI Admin.lnk');
$Shortcut.TargetPath = '%~dp0ADMIN_SIMPLE.bat';
$Shortcut.WorkingDirectory = '%~dp0';
$Shortcut.IconLocation = $IconPath;
$Shortcut.Save();
"

echo.
echo Novi shortcuts kreirani uspesno!
echo.
echo KREIRANI SHORTCUTS:
echo    T.TAXI - Glavna aplikacija
echo    TOVAR TAXI Naručilac - Dashboard za naručilac
echo    TOVAR TAXI Prevoznik - Dashboard za prevoznik  
echo    TOVAR TAXI Admin - Admin panel
echo.
echo Svi shortcuts sada koriste PNG ikone
echo.
pause
