#!/usr/bin/env python
"""
Script za kreiranje test korisnika na Render produkciji
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile

def create_test_users():
    """Kreira test korisnike za Render produkciju"""
    
    users_data = [
        {
            'username': 'marko',
            'email': 'marko@test.rs', 
            'password': 'test123',
            'role': 'prevoznik',
            'company_name': 'Marko Transport'
        },
        {
            'username': 'ana',
            'email': 'ana@test.rs',
            'password': 'test123', 
            'role': 'naručilac',
            'company_name': 'Ana Logistika'
        },
        {
            'username': 'petar',
            'email': 'petar@test.rs',
            'password': 'test123',
            'role': 'vozač',
            'company_name': 'Petar Prevoz'
        },
        {
            'username': 'stefan',
            'email': 'stefan@test.rs',
            'password': 'test123',
            'role': 'prevoznik', 
            'company_name': 'Stefan Transport'
        },
        {
            'username': 'milica',
            'email': 'milica@test.rs',
            'password': 'test123',
            'role': 'naručilac',
            'company_name': 'Milica Logistika'
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Proveri da li korisnik već postoji
        if User.objects.filter(username=user_data['username']).exists():
            print(f"Korisnik {user_data['username']} već postoji")
            continue
            
        # Kreiraj korisnika
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        
        # Kreiraj profil
        profile = Profile.objects.create(
            user=user,
            role=user_data['role'],
            company_name=user_data['company_name']
        )
        
        created_users.append(user_data['username'])
        print(f"✅ Kreiran korisnik: {user_data['username']} ({user_data['role']})")
    
    print(f"\n🎉 Ukupno kreirano {len(created_users)} korisnika")
    print("📱 Možeš testirati login sa:")
    for user_data in users_data:
        print(f"   - {user_data['username']} / test123 ({user_data['role']})")

if __name__ == '__main__':
    create_test_users()
