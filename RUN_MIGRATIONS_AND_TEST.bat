@echo off
echo ========================================
echo TOVAR TAXI - MIGRACIJE I TESTIRANJE
echo ========================================

echo.
echo 1. Kreiranje migracija za nove modele...
python manage.py makemigrations transport

echo.
echo 2. Primena migracija...
python manage.py migrate

echo.
echo 3. Kreiranje superuser-a (preskoci ako vec postoji)...
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
echo 4. Pokretanje kompletnog workflow testa...
python create_test_workflow.py

echo.
echo 5. Pokretanje development servera...
echo Pristupite aplikaciji na: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin
echo.
python manage.py runserver

pause
