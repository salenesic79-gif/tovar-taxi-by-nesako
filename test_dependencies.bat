@echo off
title TOVAR TAXI - TEST DEPENDENCIES
color 0A

echo.
echo ========================================
echo    🔧 TOVAR TAXI - TEST DEPENDENCIES
echo ========================================
echo.

cd /d "c:\Users\PC\Desktop\tovar-taxi-by-nesako"

echo 📋 Testiranje svake dependency pojedinačno...
echo.

echo 1. Testiranje Django...
pip install Django==4.2.7
if %errorlevel% neq 0 (
    echo ❌ Django - GREŠKA
) else (
    echo ✅ Django - OK
)

echo.
echo 2. Testiranje channels...
pip install channels==4.0.0
if %errorlevel% neq 0 (
    echo ❌ channels - GREŠKA
) else (
    echo ✅ channels - OK
)

echo.
echo 3. Testiranje channels-redis...
pip install channels-redis==4.1.0
if %errorlevel% neq 0 (
    echo ❌ channels-redis - GREŠKA
) else (
    echo ✅ channels-redis - OK
)

echo.
echo 4. Testiranje redis...
pip install redis==5.0.1
if %errorlevel% neq 0 (
    echo ❌ redis - GREŠKA
) else (
    echo ✅ redis - OK
)

echo.
echo 5. Testiranje python-decouple...
pip install python-decouple==3.8
if %errorlevel% neq 0 (
    echo ❌ python-decouple - GREŠKA
) else (
    echo ✅ python-decouple - OK
)

echo.
echo 6. Testiranje whitenoise...
pip install whitenoise==6.6.0
if %errorlevel% neq 0 (
    echo ❌ whitenoise - GREŠKA
) else (
    echo ✅ whitenoise - OK
)

echo.
echo 7. Testiranje gunicorn...
pip install gunicorn==21.2.0
if %errorlevel% neq 0 (
    echo ❌ gunicorn - GREŠKA
) else (
    echo ✅ gunicorn - OK
)

echo.
echo ========================================
echo    📊 TESTIRANJE ZAVRŠENO
echo ========================================
echo.
echo Pritisnite bilo koji taster za zatvaranje...
pause >nul
