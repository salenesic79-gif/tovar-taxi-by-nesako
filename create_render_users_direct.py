#!/usr/bin/env python
"""
Script za kreiranje test korisnika direktno na Render produkciji
Pokreće se sa: python create_render_users_direct.py
"""

import os
import sys
import django

# Dodaj project root u Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile

def create_test_users():
    """Kreira test korisnike za Render produkciju"""
    
    test_users = [
        {
            'username': 'marko_test',
            'email': 'marko@test.rs',
            'password': 'test123',
            'role': 'prevoznik',
            'company_name': 'Marko Transport',
            'first_name': 'Marko',
            'last_name': 'Petrović'
        },
        {
            'username': 'ana_test',
            'email': 'ana@test.rs', 
            'password': 'test123',
            'role': 'naručilac',
            'company_name': 'Ana Logistika',
            'first_name': 'Ana',
            'last_name': 'Jovanović'
        },
        {
            'username': 'petar_test',
            'email': 'petar@test.rs',
            'password': 'test123', 
            'role': 'vozač',
            'company_name': 'Petar Prevoz',
            'first_name': 'Petar',
            'last_name': 'Nikolić'
        },
        {
            'username': 'stefan_test',
            'email': 'stefan@test.rs',
            'password': 'test123',
            'role': 'prevoznik', 
            'company_name': 'Stefan Transport',
            'first_name': 'Stefan',
            'last_name': 'Mitrović'
        },
        {
            'username': 'milica_test',
            'email': 'milica@test.rs',
            'password': 'test123',
            'role': 'naručilac',
            'company_name': 'Milica Logistika', 
            'first_name': 'Milica',
            'last_name': 'Stojanović'
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        # Proveri da li korisnik već postoji
        if User.objects.filter(username=user_data['username']).exists():
            print(f"Korisnik {user_data['username']} već postoji, preskačem...")
            continue
            
        if User.objects.filter(email=user_data['email']).exists():
            print(f"Email {user_data['email']} već postoji, preskačem...")
            continue
        
        try:
            # Kreiraj korisnika
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Kreiraj profil
            profile = Profile.objects.create(
                user=user,
                role=user_data['role'],
                company_name=user_data['company_name'],
                phone_number='+381601234567',  # Dummy broj
                address='Test adresa 123, Beograd'  # Dummy adresa
            )
            
            created_users.append(user_data['username'])
            print(f"✅ Kreiran korisnik: {user_data['username']} ({user_data['role']})")
            
        except Exception as e:
            print(f"❌ Greška pri kreiranju korisnika {user_data['username']}: {str(e)}")
    
    print(f"\n🎉 Ukupno kreirano {len(created_users)} korisnika:")
    for username in created_users:
        print(f"   - {username}")
    
    # Prikaži sve korisnike u bazi
    print(f"\n📊 Svi korisnici u bazi:")
    for user in User.objects.all():
        try:
            role = user.profile.role
            print(f"   - {user.username} ({user.email}) - {role}")
        except Profile.DoesNotExist:
            print(f"   - {user.username} ({user.email}) - NEMA PROFIL")

if __name__ == '__main__':
    print("🚀 Kreiranje test korisnika za Render...")
    create_test_users()
    print("✨ Završeno!")
