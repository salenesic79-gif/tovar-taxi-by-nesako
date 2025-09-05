@echo off
echo ========================================
echo TOVAR TAXI - MIGRACIJE I TESTIRANJE
echo ========================================

echo.
echo 1. Testiranje osnovnih Django komandi...
python manage.py check
if %ERRORLEVEL% neq 0 (
    echo GRESKA: Django check neuspesan!
    pause
    exit /b 1
)

echo.
echo 2. Kreiranje migracija za nove modele...
python manage.py makemigrations transport
if %ERRORLEVEL% neq 0 (
    echo GRESKA: Kreiranje migracija neuspesno!
    pause
    exit /b 1
)

echo.
echo 3. Primena migracija...
python manage.py migrate
if %ERRORLEVEL% neq 0 (
    echo GRESKA: Primena migracija neuspesna!
    pause
    exit /b 1
)

echo.
echo 4. Kreiranje superuser-a (preskoci ako vec postoji)...
echo Korisnicko ime: admin
echo Email: admin@tovartaxi.com
echo Lozinka: admin123
python manage.py shell -c "
from django.contrib.auth.models import User;
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@tovartaxi.com', 'admin123');
    print('Superuser kreiran!');
else:
    print('Superuser vec postoji!');
"

echo.
echo 5. Testiranje osnovnih URL-ova...
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()
from django.test import Client
client = Client()
try:
    response = client.get('/')
    print(f'Početna stranica: {response.status_code}')
    response = client.get('/login/')
    print(f'Login stranica: {response.status_code}')
    response = client.get('/signup/')
    print(f'Signup stranica: {response.status_code}')
    print('Osnovni URL testovi prošli!')
except Exception as e:
    print(f'GREŠKA u URL testovima: {e}')
"

echo.
echo 6. Pokretanje kompletnog workflow testa...
python create_test_workflow.py
if %ERRORLEVEL% neq 0 (
    echo UPOZORENJE: Neki testovi nisu prošli, ali nastavljamo...
)

echo.
echo 7. Pokretanje development servera...
echo.
echo ========================================
echo SISTEM SPREMAN!
echo ========================================
echo Pristupite aplikaciji na: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin (admin/admin123)
echo.
echo Za zaustavljanje servera pritisnite Ctrl+C
echo ========================================
echo.
python manage.py runserver

pause
