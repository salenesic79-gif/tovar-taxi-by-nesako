@echo off
echo ========================================
echo    UVOZ KORISNIKA NA RENDER
echo ========================================
echo.

if not exist "users_export.json" (
    echo GREŠKA: users_export.json ne postoji!
    echo Prvo pokrenite MIGRATE_USERS_TO_RENDER.bat
    pause
    exit /b 1
)

echo PAŽNJA: Ovo će kreirati korisnike direktno na Render produkciji!
echo.
set /p confirm="Da li ste sigurni da želite da nastavite? (y/N): "
if /i not "%confirm%"=="y" (
    echo Otkazano.
    pause
    exit /b 0
)

echo.
echo Uvozim korisnike na Render...
echo.

python manage.py shell -c "
import json
import os
from django.contrib.auth.models import User
from transport.models import Profile

# Učitaj eksportovane korisnike
with open('users_export.json', 'r', encoding='utf-8') as f:
    users_data = json.load(f)

created_count = 0
skipped_count = 0
error_count = 0

for user_data in users_data:
    username = user_data['username']
    email = user_data['email']
    
    # Preskoči admin korisnike
    if user_data.get('is_superuser', False):
        print(f'PRESKAČEM admin korisnika: {username}')
        skipped_count += 1
        continue
    
    # Proveri da li korisnik već postoji
    if User.objects.filter(username=username).exists():
        print(f'POSTOJI: {username}')
        skipped_count += 1
        continue
        
    if User.objects.filter(email=email).exists():
        print(f'EMAIL POSTOJI: {email}')
        skipped_count += 1
        continue
    
    try:
        # Kreiraj korisnika sa default lozinkom
        user = User.objects.create_user(
            username=username,
            email=email,
            password='temp123',  # Privremena lozinka
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
            is_active=user_data.get('is_active', True)
        )
        
        # Kreiraj profil
        profile = Profile.objects.create(
            user=user,
            role=user_data.get('role', 'naručilac'),
            company_name=user_data.get('company_name', ''),
            phone_number=user_data.get('phone_number', ''),
            address=user_data.get('address', '')
        )
        
        print(f'✅ KREIRAN: {username} ({user_data.get(\"role\", \"naručilac\")})')
        created_count += 1
        
    except Exception as e:
        print(f'❌ GREŠKA za {username}: {str(e)}')
        error_count += 1

print(f'')
print(f'📊 REZULTAT:')
print(f'   ✅ Kreirano: {created_count}')
print(f'   ⏭️  Preskočeno: {skipped_count}')
print(f'   ❌ Greške: {error_count}')
print(f'')

if created_count > 0:
    print('⚠️  VAŽNO: Svi korisnici imaju privremenu lozinku \"temp123\"')
    print('   Korisnici treba da promene lozinku preko \"Zaboravili ste lozinku?\"')
"

if %ERRORLEVEL% NEQ 0 (
    echo GREŠKA pri uvozu korisnika!
    pause
    exit /b 1
)

echo.
echo ========================================
echo           MIGRACIJA ZAVRŠENA
echo ========================================
echo.
echo Korisnici su uspešno uvezeni na Render!
echo.
echo SLEDEĆI KORACI:
echo 1. Obavestite korisnike da koriste privremenu lozinku "temp123"
echo 2. Korisnici treba da promene lozinku preko "Zaboravili ste lozinku?"
echo 3. Testiranje login funkcionalnosti na Render-u
echo.
pause
