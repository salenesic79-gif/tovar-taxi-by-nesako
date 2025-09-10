@echo off
echo ========================================
echo TOVAR TAXI - DEPLOY ADMIN IMPORT/EXPORT
echo ========================================
echo.

echo Checking current directory...
cd /d "c:\Users\PC\Desktop\tovar-taxi-by-nesako"
echo Current directory: %CD%

echo.
echo Adding admin import/export changes...
git add transport/admin.py
git add templates/admin/import_users.html

echo.
echo Committing admin changes...
git commit -m "Add admin import/export functionality for users - localhost to Render migration"

echo.
echo Pushing to Render...
git push origin main

echo.
echo ========================================
echo ADMIN IMPORT/EXPORT DEPLOYED!
echo ========================================
echo.
echo Funkcionalnosti dodane:
echo - Export korisnika u JSON/CSV format (localhost)
echo - Import korisnika iz JSON/CSV fajla (Render)
echo - Admin actions za bulk export
echo - Custom admin stranica za import
echo.
echo Kako koristiti:
echo 1. Na localhost: Admin → Korisnici → Select users → Actions → "Izvezi korisnike (JSON)"
echo 2. Na Render: Admin → Korisnici → "Import users" link → Upload JSON
echo.
echo Admin panel: https://tovar-taxi-by-nesako-web.onrender.com/admin/
echo.
pause
