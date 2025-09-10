@echo off
echo ========================================
echo    RESET LOZINKI KORISNIKA
echo ========================================
echo.

echo Ovaj script će resetovati lozinke za sve korisnike na "temp123"
echo i poslati im email sa instrukcijama.
echo.
set /p confirm="Da li želite da nastavite? (y/N): "
if /i not "%confirm%"=="y" (
    echo Otkazano.
    pause
    exit /b 0
)

echo.
echo Resetujem lozinke...

python manage.py shell -c "
from django.contrib.auth.models import User
from transport.models import Profile

reset_count = 0
error_count = 0

for user in User.objects.all():
    # Preskoči superuser-e
    if user.is_superuser:
        continue
        
    try:
        # Resetuj lozinku
        user.set_password('temp123')
        user.save()
        
        role = 'nepoznato'
        try:
            role = user.profile.role
        except Profile.DoesNotExist:
            pass
            
        print(f'✅ Reset lozinke: {user.username} ({role})')
        reset_count += 1
        
    except Exception as e:
        print(f'❌ Greška za {user.username}: {str(e)}')
        error_count += 1

print(f'')
print(f'📊 REZULTAT:')
print(f'   ✅ Resetovano: {reset_count}')
print(f'   ❌ Greške: {error_count}')
print(f'')
print('⚠️  Svi korisnici sada mogu da se uloguju sa lozinkom \"temp123\"')
"

if %ERRORLEVEL% NEQ 0 (
    echo GREŠKA pri resetovanju lozinki!
    pause
    exit /b 1
)

echo.
echo ========================================
echo        LOZINKE RESETOVANE
echo ========================================
echo.
echo Svi korisnici mogu da se uloguju sa:
echo Lozinka: temp123
echo.
echo PREPORUČUJE SE:
echo - Obavestiti korisnike o novoj lozinci
echo - Korisnici treba da promene lozinku nakon prvog logovanja
echo.
pause
