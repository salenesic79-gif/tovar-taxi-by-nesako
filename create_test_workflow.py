#!/usr/bin/env python
"""
Test skript za kompletan workflow Tovar Taxi aplikacije
Testira sve funkcionalnosti od početne stranice do finalizovanih B2B funkcija
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
django.setup()

from transport.models import (
    Profile, Vehicle, Shipment, InstantDelivery, FoodDelivery, 
    PaymentReservation, PremiumSubscription, DriverLocation
)

class TovarTaxiWorkflowTest:
    def __init__(self):
        self.client = Client()
        self.test_users = {}
        
    def setup_test_users(self):
        """Kreiranje test korisnika"""
        print("🔧 Kreiranje test korisnika...")
        
        # Test naručilac
        naručilac = User.objects.create_user(
            username='test_naručilac',
            email='naručilac@test.com',
            password='test123',
            first_name='Marko',
            last_name='Petrović'
        )
        Profile.objects.create(
            user=naručilac,
            role='naručilac',
            phone_number='+381601234567',
            address='Beograd, Srbija',
            company_name='Test Firma DOO'
        )
        self.test_users['naručilac'] = naručilac
        
        # Test prevoznik
        prevoznik = User.objects.create_user(
            username='test_prevoznik',
            email='prevoznik@test.com',
            password='test123',
            first_name='Stefan',
            last_name='Nikolić'
        )
        Profile.objects.create(
            user=prevoznik,
            role='prevoznik',
            phone_number='+381602345678',
            address='Novi Sad, Srbija',
            company_name='Transport NS',
            vozačka_dozvola='B,C,E',
            tip_vozila='kamion'
        )
        Vehicle.objects.create(
            owner=prevoznik,
            vehicle_type='kamion',
            license_plate='BG-123-AB',
            capacity=5000,
            is_available=True
        )
        self.test_users['prevoznik'] = prevoznik
        
        # Test vozač
        vozač = User.objects.create_user(
            username='test_vozač',
            email='vozač@test.com',
            password='test123',
            first_name='Miloš',
            last_name='Jovanović'
        )
        Profile.objects.create(
            user=vozač,
            role='vozač',
            phone_number='+381603456789',
            address='Kragujevac, Srbija'
        )
        self.test_users['vozač'] = vozač
        
        print("✅ Test korisnici kreirani")
    
    def test_home_page(self):
        """Test početne stranice"""
        print("\n🏠 Testiranje početne stranice...")
        
        response = self.client.get('/')
        assert response.status_code == 200, f"Početna stranica nije dostupna: {response.status_code}"
        assert 'Tovar Taxi' in response.content.decode(), "Naslov nije pronađen na početnoj stranici"
        
        print("✅ Početna stranica radi")
    
    def test_registration_workflow(self):
        """Test registracije za oba tipa korisnika"""
        print("\n📝 Testiranje registracije...")
        
        # Test signup stranica
        response = self.client.get('/signup/')
        assert response.status_code == 200, "Signup stranica nije dostupna"
        
        # Test naručilac registracija
        response = self.client.get('/signup/sender/')
        assert response.status_code == 200, "Naručilac signup stranica nije dostupna"
        
        # Test prevoznik registracija  
        response = self.client.get('/signup/carrier/')
        assert response.status_code == 200, "Prevoznik signup stranica nije dostupna"
        
        print("✅ Registracija stranice rade")
    
    def test_login_workflow(self):
        """Test login funkcionalnosti sa role-based redirect"""
        print("\n🔐 Testiranje login workflow-a...")
        
        # Test login stranica
        response = self.client.get('/login/')
        assert response.status_code == 200, "Login stranica nije dostupna"
        
        # Test login naručioca
        login_success = self.client.login(username='test_naručilac', password='test123')
        assert login_success, "Login naručioca neuspešan"
        
        # Test redirect na shipper dashboard
        response = self.client.get('/login/', follow=True)
        self.client.logout()
        
        # Test login prevoznika
        login_success = self.client.login(username='test_prevoznik', password='test123')
        assert login_success, "Login prevoznika neuspešan"
        self.client.logout()
        
        print("✅ Login workflow radi")
    
    def test_post_registration_workflow(self):
        """Test post-registration stranica"""
        print("\n🚀 Testiranje post-registration workflow-a...")
        
        # Login kao naručilac
        self.client.login(username='test_naručilac', password='test123')
        
        # Test create shipment request
        response = self.client.get('/create-shipment-request/')
        assert response.status_code == 200, "Create shipment request stranica nije dostupna"
        
        self.client.logout()
        
        # Login kao prevoznik
        self.client.login(username='test_prevoznik', password='test123')
        
        # Test create route availability
        response = self.client.get('/create-route-availability/')
        assert response.status_code == 200, "Create route availability stranica nije dostupna"
        
        self.client.logout()
        
        print("✅ Post-registration workflow radi")
    
    def test_b2b_functionality(self):
        """Test B2B funkcionalnosti"""
        print("\n💼 Testiranje B2B funkcionalnosti...")
        
        # Login kao naručilac
        self.client.login(username='test_naručilac', password='test123')
        
        # Test premium subscription
        response = self.client.get('/premium-subscription/')
        assert response.status_code == 200, "Premium subscription stranica nije dostupna"
        
        # Test kreiranje premium pretplate
        response = self.client.post('/premium-subscription/', {
            'subscription_type': 'premium'
        })
        
        # Proveri da li je pretplata kreirana
        subscription = PremiumSubscription.objects.filter(user=self.test_users['naručilac']).first()
        assert subscription is not None, "Premium pretplata nije kreirana"
        assert subscription.subscription_type == 'premium', "Pogrešan tip pretplate"
        
        self.client.logout()
        
        print("✅ B2B funkcionalnosti rade")
    
    def test_instant_delivery(self):
        """Test instant delivery funkcionalnosti"""
        print("\n⚡ Testiranje instant delivery...")
        
        # Login kao naručilac
        self.client.login(username='test_naručilac', password='test123')
        
        # Test instant delivery stranica
        response = self.client.get('/instant-delivery/')
        assert response.status_code == 200, "Instant delivery stranica nije dostupna"
        
        # Test kreiranje instant delivery
        response = self.client.post('/instant-delivery/', {
            'pickup_address': 'Knez Mihailova 1, Beograd',
            'delivery_address': 'Trg Republike 5, Beograd', 
            'delivery_type': 'express',
            'item_description': 'Test paket',
            'estimated_weight': '2.5',
            'special_instructions': 'Pažljivo rukovati'
        })
        
        # Proveri da li je delivery kreiran
        delivery = InstantDelivery.objects.filter(sender=self.test_users['naručilac']).first()
        assert delivery is not None, "Instant delivery nije kreiran"
        
        # Proveri da li je payment reservation kreirana
        payment = PaymentReservation.objects.filter(
            transaction_id__contains=f"ID-{delivery.id}"
        ).first()
        assert payment is not None, "Payment reservation nije kreirana"
        
        self.client.logout()
        
        print("✅ Instant delivery radi")
    
    def test_food_delivery(self):
        """Test food delivery funkcionalnosti"""
        print("\n🍕 Testiranje food delivery...")
        
        # Login kao naručilac
        self.client.login(username='test_naručilac', password='test123')
        
        # Test food delivery stranica
        response = self.client.get('/food-delivery/')
        assert response.status_code == 200, "Food delivery stranica nije dostupna"
        
        # Test kreiranje food delivery
        test_items = [
            {'name': 'Pizza Margarita', 'price': 800, 'quantity': 1},
            {'name': 'Coca Cola', 'price': 150, 'quantity': 2}
        ]
        
        response = self.client.post('/food-delivery/', {
            'restaurant_name': 'Test Restoran',
            'restaurant_address': 'Makedonska 10, Beograd',
            'delivery_address': 'Knez Mihailova 1, Beograd',
            'customer_phone': '+381601234567',
            'items': json.dumps(test_items),
            'total_amount': '1100',
            'special_instructions': 'Bez luka'
        })
        
        # Proveri da li je food delivery kreiran
        food_order = FoodDelivery.objects.filter(customer=self.test_users['naručilac']).first()
        assert food_order is not None, "Food delivery nije kreiran"
        
        self.client.logout()
        
        print("✅ Food delivery radi")
    
    def test_driver_functionality(self):
        """Test driver funkcionalnosti"""
        print("\n🚗 Testiranje driver funkcionalnosti...")
        
        # Login kao vozač
        self.client.login(username='test_vozač', password='test123')
        
        # Test driver dashboard extended
        response = self.client.get('/driver-dashboard-extended/')
        assert response.status_code == 200, "Driver dashboard extended nije dostupan"
        
        # Test location update
        response = self.client.post('/update-location/', {
            'latitude': '44.8176',
            'longitude': '20.4633',
            'accuracy': '10.0',
            'speed': '0.0',
            'heading': '0.0'
        })
        
        result = json.loads(response.content.decode())
        assert result['success'] == True, "Location update neuspešan"
        
        # Proveri da li je lokacija kreirana
        location = DriverLocation.objects.filter(driver=self.test_users['vozač']).first()
        assert location is not None, "Driver location nije kreirana"
        
        self.client.logout()
        
        print("✅ Driver funkcionalnosti rade")
    
    def test_dashboard_access(self):
        """Test pristupa dashboard-ima"""
        print("\n📊 Testiranje dashboard pristupa...")
        
        # Test naručilac dashboard
        self.client.login(username='test_naručilac', password='test123')
        response = self.client.get('/shipper-dashboard/')
        assert response.status_code == 200, "Shipper dashboard nije dostupan"
        self.client.logout()
        
        # Test prevoznik dashboard
        self.client.login(username='test_prevoznik', password='test123')
        response = self.client.get('/carrier-dashboard/')
        assert response.status_code == 200, "Carrier dashboard nije dostupan"
        self.client.logout()
        
        print("✅ Dashboard pristup radi")
    
    def run_all_tests(self):
        """Pokretanje svih testova"""
        print("🚀 Pokretanje kompletnog workflow testa za Tovar Taxi\n")
        
        try:
            self.setup_test_users()
            self.test_home_page()
            self.test_registration_workflow()
            self.test_login_workflow()
            self.test_post_registration_workflow()
            self.test_b2b_functionality()
            self.test_instant_delivery()
            self.test_food_delivery()
            self.test_driver_functionality()
            self.test_dashboard_access()
            
            print("\n🎉 SVI TESTOVI USPEŠNO ZAVRŠENI!")
            print("✅ Kompletan workflow od početne do trenutne tačke radi ispravno")
            
        except Exception as e:
            print(f"\n❌ TEST NEUSPEŠAN: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

if __name__ == '__main__':
    tester = TovarTaxiWorkflowTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
