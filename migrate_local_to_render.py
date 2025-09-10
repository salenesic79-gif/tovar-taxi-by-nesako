#!/usr/bin/env python
"""
Script za migraciju lokalnih korisnika u Render PostgreSQL bazu
Pokreće se sa: python migrate_local_to_render.py
"""

import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile

def export_local_users():
    """Eksportuje lokalne korisnike u JSON format"""
    print("📤 Eksportovanje lokalnih korisnika...")
    
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
            print(f"   ✅ {user.username} ({profile.role})")
        except Profile.DoesNotExist:
            print(f"   ⚠️  {user.username} - nema profil")
    
    # Sačuvaj u JSON
    with open('users_for_render.json', 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Eksportovano {len(users_data)} korisnika u users_for_render.json")
    return len(users_data)

def import_users_to_render():
    """Uvozi korisnike u Render bazu (PostgreSQL)"""
    
    if not os.path.exists('users_for_render.json'):
        print("❌ users_for_render.json ne postoji!")
        return False
    
    print("📥 Uvozim korisnike u Render bazu...")
    
    with open('users_for_render.json', 'r', encoding='utf-8') as f:
        users_data = json.load(f)
    
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for user_data in users_data:
        username = user_data['username']
        email = user_data['email']
        
        # Preskoči superuser-e
        if user_data.get('is_superuser', False):
            print(f"   ⏭️  {username} - admin korisnik, preskačem")
            skipped_count += 1
            continue
        
        # Proveri da li korisnik već postoji
        if User.objects.filter(username=username).exists():
            print(f"   ⏭️  {username} - već postoji")
            skipped_count += 1
            continue
            
        if User.objects.filter(email=email).exists():
            print(f"   ⏭️  {email} - email već postoji")
            skipped_count += 1
            continue
        
        try:
            # Kreiraj korisnika
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
            
            print(f"   ✅ {username} ({user_data.get('role', 'naručilac')})")
            created_count += 1
            
        except Exception as e:
            print(f"   ❌ Greška za {username}: {str(e)}")
            error_count += 1
    
    print(f"\n📊 REZULTAT:")
    print(f"   ✅ Kreirano: {created_count}")
    print(f"   ⏭️  Preskočeno: {skipped_count}")
    print(f"   ❌ Greške: {error_count}")
    
    if created_count > 0:
        print(f"\n⚠️  VAŽNO: Svi korisnici imaju privremenu lozinku 'temp123'")
        print(f"   Korisnici mogu da promene lozinku preko 'Zaboravili ste lozinku?'")
    
    return created_count > 0

def main():
    print("🚀 MIGRACIJA KORISNIKA SA LOKALNE NA RENDER BAZU")
    print("=" * 50)
    
    # Proveri da li je ovo lokalna ili Render baza
    db_engine = os.environ.get('DATABASE_URL', '')
    if 'postgres' in db_engine:
        print("🔗 Povezan na PostgreSQL (Render)")
        # Uvezi korisnike
        import_users_to_render()
    else:
        print("💾 Povezan na SQLite (lokalno)")
        # Eksportuj korisnike
        export_local_users()
        print("\n📋 SLEDEĆI KORAK:")
        print("1. Postavi DATABASE_URL environment varijablu za Render")
        print("2. Pokreni script ponovo da uvezem korisnike")

if __name__ == '__main__':
    main()
