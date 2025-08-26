#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile, Vehicle

def create_test_users():
    print("Kreiranje test korisnika...")
    
    # Create superuser
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@tovartaxi.rs',
            password='admin123'
        )
        print("✅ Admin kreiran: username=admin, password=admin123")
    else:
        print("ℹ️ Admin već postoji")
    
    # Create test naručilac transporta
    if not User.objects.filter(username='naruci').exists():
        naruci = User.objects.create_user(
            username='naruci',
            email='naruci@test.rs',
            password='test123',
            first_name='Marko',
            last_name='Petrović'
        )
        Profile.objects.create(
            user=naruci,
            user_type='shipper',
            phone_number='+381641234567',
            address='Knez Mihailova 42, Beograd',
            company_name='Petrović Transport DOO',
            tax_number='123456789',
            is_verified=True
        )
        print("✅ Naručilac transporta kreiran: username=naruci, password=test123")
    else:
        print("ℹ️ Naručilac transporta već postoji")
    
    # Create test prevoznik
    if not User.objects.filter(username='prevoz').exists():
        prevoz = User.objects.create_user(
            username='prevoz',
            email='prevoz@test.rs',
            password='test123',
            first_name='Stefan',
            last_name='Nikolić'
        )
        profile = Profile.objects.create(
            user=prevoz,
            user_type='carrier',
            phone_number='+381651234567',
            address='Bulevar Oslobođenja 15, Novi Sad',
            company_name='Nikolić Prevoz DOO',
            tax_number='987654321',
            is_verified=True
        )
        
        # Add test vehicle for prevoznik
        Vehicle.objects.create(
            owner=prevoz,
            vehicle_type='truck',
            license_plate='BG-123-AB',
            max_weight=5000.00,
            max_volume=25.00,
            length=6.00,
            width=2.50,
            height=2.80,
            is_active=True
        )
        print("✅ Prevoznik kreiran: username=prevoz, password=test123")
        print("✅ Test vozilo dodato za prevoznika")
    else:
        print("ℹ️ Prevoznik već postoji")
    
    print("\n🎉 SVI TEST KORISNICI KREIRANI!")
    print("\n📋 PRISTUPNI PODACI:")
    print("👨‍💼 Admin: username=admin, password=admin123")
    print("📦 Naručilac: username=naruci, password=test123")
    print("🚛 Prevoznik: username=prevoz, password=test123")

if __name__ == '__main__':
    create_test_users()
