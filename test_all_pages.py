#!/usr/bin/env python
"""
TOVAR TAXI - KOMPLETNO TESTIRANJE SVIH STRANICA
Automatsko testiranje svih URL-ova i funkcionalnosti
"""

import os
import sys
import django
import requests
from urllib.parse import urljoin

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile, Vehicle, Shipment

BASE_URL = 'http://localhost:8000'

def test_page(url, description, expected_status=200):
    """Test pojedinačne stranice"""
    try:
        full_url = urljoin(BASE_URL, url)
        response = requests.get(full_url, timeout=10)
        
        if response.status_code == expected_status:
            print(f"✅ {description}: {response.status_code}")
            return True
        else:
            print(f"❌ {description}: {response.status_code} (očekivano {expected_status})")
            return False
    except Exception as e:
        print(f"❌ {description}: GREŠKA - {str(e)}")
        return False

def test_all_pages():
    """Testiraj sve stranice aplikacije"""
    print("🚀 TESTIRANJE SVIH STRANICA TOVAR TAXI APLIKACIJE")
    print("=" * 60)
    
    # Test osnovnih stranica
    pages = [
        ('/', 'Početna stranica'),
        ('/admin/', 'Admin panel'),
        ('/signup/', 'Registracija'),
        ('/signup/sender/', 'Registracija naručioca'),
        ('/signup/carrier/', 'Registracija prevoznika'),
        ('/login/', 'Prijava', 302),  # Redirect to login form
        ('/dashboard/', 'Dashboard', 302),  # Requires login
        ('/create-shipment/', 'Kreiranje pošiljke', 302),  # Requires login
        ('/freight-exchange/', 'Freight Exchange', 302),  # Requires login
        ('/vehicles/', 'Upravljanje vozilima', 302),  # Requires login
        ('/settings/', 'Podešavanja', 302),  # Requires login
        ('/terms/', 'Uslovi korišćenja'),
    ]
    
    successful_tests = 0
    total_tests = len(pages)
    
    for url, description, *expected in pages:
        expected_status = expected[0] if expected else 200
        if test_page(url, description, expected_status):
            successful_tests += 1
    
    print("\n" + "=" * 60)
    print(f"📊 REZULTATI TESTIRANJA")
    print("=" * 60)
    print(f"✅ Uspešno: {successful_tests}/{total_tests}")
    print(f"❌ Neuspešno: {total_tests - successful_tests}/{total_tests}")
    print(f"📈 Procenat uspešnosti: {(successful_tests/total_tests)*100:.1f}%")
    
    # Test baze podataka
    print(f"\n📊 STANJE BAZE PODATAKA:")
    print(f"👥 Korisnici: {User.objects.count()}")
    print(f"📋 Profili: {Profile.objects.count()}")
    print(f"🚛 Vozila: {Vehicle.objects.count()}")
    print(f"📦 Pošiljke: {Shipment.objects.count()}")
    
    if successful_tests == total_tests:
        print(f"\n🎉 SVI TESTOVI PROŠLI USPEŠNO!")
        print(f"🚀 TOVAR TAXI APLIKACIJA JE POTPUNO FUNKCIONALNA!")
    else:
        print(f"\n⚠️ NEKI TESTOVI NISU PROŠLI - POTREBNE SU ISPRAVKE")
    
    return successful_tests == total_tests

if __name__ == '__main__':
    test_all_pages()
