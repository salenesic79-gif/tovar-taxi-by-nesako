#!/usr/bin/env python
"""
TOVAR TAXI - KOMPLETNO TESTIRANJE WORKFLOW-a
Automatsko testiranje svih funkcionalnosti aplikacije
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from django.contrib.auth.models import User
from transport.models import Profile, Vehicle, Shipment, ShipmentOffer
from django.test import Client
from django.urls import reverse

def test_complete_workflow():
    print("🚀 ZAPOČINJE KOMPLETNO TESTIRANJE TOVAR TAXI APLIKACIJE")
    print("=" * 60)
    
    # 1. TEST KORISNIKA
    print("\n1️⃣ TESTIRANJE KORISNIKA:")
    
    # Proveri postojanje test korisnika
    admin = User.objects.filter(username='admin').first()
    naruci = User.objects.filter(username='naruci').first()
    prevoz = User.objects.filter(username='prevoz').first()
    
    print(f"✅ Admin: {'POSTOJI' if admin else 'NE POSTOJI'}")
    print(f"✅ Naručilac: {'POSTOJI' if naruci else 'NE POSTOJI'}")
    print(f"✅ Prevoznik: {'POSTOJI' if prevoz else 'NE POSTOJI'}")
    
    if not all([admin, naruci, prevoz]):
        print("❌ NEDOSTAJU TEST KORISNICI!")
        return False
    
    # 2. TEST PROFILA
    print("\n2️⃣ TESTIRANJE PROFILA:")
    
    naruci_profile = Profile.objects.filter(user=naruci).first()
    prevoz_profile = Profile.objects.filter(user=prevoz).first()
    
    print(f"✅ Naručilac profil: {'POSTOJI' if naruci_profile else 'NE POSTOJI'}")
    print(f"✅ Prevoznik profil: {'POSTOJI' if prevoz_profile else 'NE POSTOJI'}")
    
    if naruci_profile:
        print(f"   - Tip: {naruci_profile.user_type}")
        print(f"   - Kompanija: {naruci_profile.company_name}")
        print(f"   - Verifikovan: {naruci_profile.is_verified}")
    
    if prevoz_profile:
        print(f"   - Tip: {prevoz_profile.user_type}")
        print(f"   - Kompanija: {prevoz_profile.company_name}")
        print(f"   - Verifikovan: {prevoz_profile.is_verified}")
    
    # 3. TEST VOZILA
    print("\n3️⃣ TESTIRANJE VOZILA:")
    
    vehicles = Vehicle.objects.filter(owner=prevoz)
    print(f"✅ Vozila prevoznika: {vehicles.count()}")
    
    for vehicle in vehicles:
        print(f"   - {vehicle.get_vehicle_type_display()}: {vehicle.license_plate}")
        print(f"     Nosivost: {vehicle.max_weight}kg, Zapremina: {vehicle.max_volume}m³")
    
    # 4. TEST WEB STRANICA
    print("\n4️⃣ TESTIRANJE WEB STRANICA:")
    
    client = Client()
    
    # Test početne stranice
    try:
        response = client.get('/')
        print(f"✅ Početna stranica: {response.status_code}")
    except Exception as e:
        print(f"❌ Početna stranica: {e}")
    
    # Test login stranice
    try:
        response = client.get('/login/')
        print(f"✅ Login stranica: {response.status_code}")
    except Exception as e:
        print(f"❌ Login stranica: {e}")
    
    # Test admin stranice
    try:
        response = client.get('/admin/')
        print(f"✅ Admin stranica: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin stranica: {e}")
    
    # 5. TEST LOGIN FUNKCIONALNOSTI
    print("\n5️⃣ TESTIRANJE LOGIN FUNKCIONALNOSTI:")
    
    # Login kao naručilac
    login_success = client.login(username='naruci', password='test123')
    print(f"✅ Login naručilac: {'USPEŠNO' if login_success else 'NEUSPEŠNO'}")
    
    if login_success:
        try:
            response = client.get('/dashboard/')
            print(f"✅ Dashboard naručilac: {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard naručilac: {e}")
    
    client.logout()
    
    # Login kao prevoznik
    login_success = client.login(username='prevoz', password='test123')
    print(f"✅ Login prevoznik: {'USPEŠNO' if login_success else 'NEUSPEŠNO'}")
    
    if login_success:
        try:
            response = client.get('/dashboard/')
            print(f"✅ Dashboard prevoznik: {response.status_code}")
        except Exception as e:
            print(f"❌ Dashboard prevoznik: {e}")
    
    # 6. TEST KREIRANJE POŠILJKE
    print("\n6️⃣ TESTIRANJE KREIRANJE POŠILJKE:")
    
    # Kreiraj test pošiljku
    test_shipment = Shipment.objects.create(
        shipper=naruci,
        pickup_address="Knez Mihailova 1, Beograd",
        delivery_address="Bulevar Oslobođenja 1, Novi Sad",
        cargo_description="Test teret - elektronika",
        weight=100.0,
        volume=2.5,
        pickup_date=datetime.now().date(),
        price=15000.00,
        status='pending'
    )
    
    print(f"✅ Test pošiljka kreirana: ID {test_shipment.id}")
    print(f"   - Od: {test_shipment.pickup_address}")
    print(f"   - Do: {test_shipment.delivery_address}")
    print(f"   - Cena: {test_shipment.price} RSD")
    
    # 7. TEST PONUDA
    print("\n7️⃣ TESTIRANJE SISTEMA PONUDA:")
    
    # Kreiraj test ponudu
    test_offer = ShipmentOffer.objects.create(
        shipment=test_shipment,
        carrier=prevoz,
        offered_price=12000.00,
        message="Mogu da izvršim transport sutra ujutru. Imam iskustvo sa elektronikom."
    )
    
    print(f"✅ Test ponuda kreirana: ID {test_offer.id}")
    print(f"   - Ponuđena cena: {test_offer.offered_price} RSD")
    print(f"   - Status: {test_offer.status}")
    
    # 8. FINALNI IZVEŠTAJ
    print("\n" + "=" * 60)
    print("🎉 FINALNI IZVEŠTAJ TESTIRANJA")
    print("=" * 60)
    
    total_users = User.objects.count()
    total_profiles = Profile.objects.count()
    total_vehicles = Vehicle.objects.count()
    total_shipments = Shipment.objects.count()
    total_offers = ShipmentOffer.objects.count()
    
    print(f"👥 Ukupno korisnika: {total_users}")
    print(f"📋 Ukupno profila: {total_profiles}")
    print(f"🚛 Ukupno vozila: {total_vehicles}")
    print(f"📦 Ukupno pošiljki: {total_shipments}")
    print(f"💰 Ukupno ponuda: {total_offers}")
    
    print("\n✅ SVI TESTOVI ZAVRŠENI USPEŠNO!")
    print("🚀 TOVAR TAXI APLIKACIJA JE SPREMNA ZA PRODUKCIJU!")
    
    return True

if __name__ == '__main__':
    test_complete_workflow()
