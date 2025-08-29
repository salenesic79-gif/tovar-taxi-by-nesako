@echo off
title TOVAR TAXI - FINALNO POKRETANJE
color 0A

echo.
echo ========================================
echo    🚛 TOVAR TAXI - FINALNO POKRETANJE
echo ========================================
echo.

cd /d "c:\Users\PC\Desktop\tovar-taxi-by-nesako"

echo 🔧 Instaliranje dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ GREŠKA: Problem sa instaliranjem dependencies!
    echo Pritisnite bilo koji taster za nastavak...
    pause >nul
) else (
    echo ✅ Dependencies uspešno instalirani!
)

echo.
echo 🗄️ Pokretanje migracija...
python manage.py makemigrations
if %errorlevel% neq 0 (
    echo ❌ GREŠKA: Problem sa makemigrations!
    echo Pritisnite bilo koji taster za nastavak...
    pause >nul
)

python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ GREŠKA: Problem sa migrate!
    echo Pritisnite bilo koji taster za nastavak...
    pause >nul
) else (
    echo ✅ Migracije uspešno završene!
)

echo.
echo 👥 Kreiranje test korisnika...
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile, Vehicle

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print('✅ Admin kreiran: admin/admin123')

# Create shipper
if not User.objects.filter(username='narucilac').exists():
    shipper = User.objects.create_user('narucilac', 'shipper@test.com', 'test123')
    shipper.first_name = 'Marko'
    shipper.last_name = 'Petrović'
    shipper.save()
    Profile.objects.create(user=shipper, role='naručilac', phone_number='+381601234567', company_name='ABC Transport d.o.o.')
    print('✅ Naručilac kreiran: narucilac/test123')

# Create carrier
if not User.objects.filter(username='prevoznik').exists():
    carrier = User.objects.create_user('prevoznik', 'carrier@test.com', 'test123')
    carrier.first_name = 'Stefan'
    carrier.last_name = 'Nikolić'
    carrier.save()
    profile = Profile.objects.create(user=carrier, role='prevoznik', phone_number='+381607654321', company_name='Brzi Transport d.o.o.')
    
    # Add vehicles
    Vehicle.objects.create(owner=carrier, vehicle_type='kamion', license_plate='BG-123-AB', capacity=10.0, volume=40.0)
    Vehicle.objects.create(owner=carrier, vehicle_type='šleper', license_plate='BG-456-CD', capacity=25.0, volume=90.0)
    print('✅ Prevoznik kreiran: prevoznik/test123')

# Create driver
if not User.objects.filter(username='vozac').exists():
    driver = User.objects.create_user('vozac', 'driver@test.com', 'test123')
    driver.first_name = 'Milan'
    driver.last_name = 'Jovanović'
    driver.save()
    Profile.objects.create(user=driver, role='vozač', phone_number='+381609876543')
    print('✅ Vozač kreiran: vozac/test123')
"

if %errorlevel% neq 0 (
    echo ❌ GREŠKA: Problem sa kreiranjem test korisnika!
    echo Pritisnite bilo koji taster za nastavak...
    pause >nul
) else (
    echo ✅ Test korisnici uspešno kreirani!
)

echo.
echo 🚀 Pokretanje Django servera...
echo.
echo 🌐 PRISTUP:
echo    Lokalno: http://localhost:8000
echo    Mrežno:  http://192.168.0.21:8000
echo.
echo 👤 TEST NALOZI:
echo    Admin:     admin / admin123
echo    Naručilac: narucilac / test123
echo    Prevoznik: prevoznik / test123
echo    Vozač:     vozac / test123
echo.
echo Pritisnite bilo koji taster za pokretanje servera...
pause >nul

start http://localhost:8000
python manage.py runserver 0.0.0.0:8000

echo.
echo Pritisnite bilo koji taster za zatvaranje...
pause >nul
