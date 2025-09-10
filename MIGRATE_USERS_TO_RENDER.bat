@echo off
echo ========================================
echo    MIGRACIJA KORISNIKA NA RENDER
echo ========================================
echo.

echo Eksportovanje korisnika iz lokalne baze...
python manage.py shell -c "
import json
from django.contrib.auth.models import User
from transport.models import Profile

users_data = []
for user in User.objects.all():
    try:
        profile = user.profile
        user_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'role': profile.role,
            'company_name': profile.company_name,
            'phone_number': profile.phone_number,
            'address': profile.address
        }
        users_data.append(user_data)
        print(f'Eksportovan: {user.username} ({profile.role})')
    except Profile.DoesNotExist:
        print(f'GREŠKA: {user.username} nema profil')

with open('users_export.json', 'w', encoding='utf-8') as f:
    json.dump(users_data, f, ensure_ascii=False, indent=2)

print(f'Ukupno eksportovano {len(users_data)} korisnika u users_export.json')
"

if %ERRORLEVEL% NEQ 0 (
    echo GREŠKA pri eksportovanju korisnika!
    pause
    exit /b 1
)

echo.
echo Korisnici su eksportovani u users_export.json
echo.
echo SLEDEĆI KORAK:
echo 1. Otvorite users_export.json i proverite podatke
echo 2. Pokrenite IMPORT_USERS_TO_RENDER.bat da uvezete korisnike na Render
echo.
pause
