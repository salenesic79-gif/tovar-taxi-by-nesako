#!/usr/bin/env python3
"""
Test Mode with Ngrok Setup for Tovar Taxi
Allows external access to the application for testing and demo purposes
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.append(str(project_dir))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tovar_taxi.settings')
import django
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from transport.models import Profile, Cargo, Notification, CenaPoKilometrazi
from transport.utils import create_base_prices

class NgrokTestMode:
    def __init__(self):
        self.ngrok_process = None
        self.django_process = None
        self.public_url = None
        self.test_mode_active = False
        
    def check_ngrok_installed(self):
        """Check if ngrok is installed"""
        try:
            result = subprocess.run(['ngrok', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Ngrok is installed:", result.stdout.strip())
                return True
            else:
                print("❌ Ngrok not found or error:", result.stderr)
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Ngrok is not installed or not in PATH")
            print("📥 Download ngrok from: https://ngrok.com/download")
            return False
    
    def setup_test_environment(self):
        """Setup test environment with demo data"""
        print("🔧 Setting up test environment...")
        
        # Create test users if they don't exist
        self.create_test_users()
        
        # Create base prices
        if not CenaPoKilometrazi.objects.exists():
            create_base_prices()
            print("✅ Base prices created")
        
        # Create demo cargo if none exists
        self.create_demo_cargo()
        
        print("✅ Test environment ready")
    
    def create_test_users(self):
        """Create test users for demo"""
        users_data = [
            {
                'username': 'demo_shipper',
                'email': 'shipper@demo.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'Naručilac',
                'role': 'naručilac'
            },
            {
                'username': 'demo_carrier',
                'email': 'carrier@demo.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'Prevoznik',
                'role': 'prevoznik'
            },
            {
                'username': 'demo_admin',
                'email': 'admin@demo.com',
                'password': 'demo123',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'role': 'naručilac',
                'is_staff': True,
                'is_superuser': True
            }
        ]
        
        for user_data in users_data:
            username = user_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                
                if user_data.get('is_staff'):
                    user.is_staff = True
                if user_data.get('is_superuser'):
                    user.is_superuser = True
                user.save()
                
                # Create profile
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': user_data['role'],
                        'phone_number': '+381601234567',
                        'address': 'Demo adresa, Beograd'
                    }
                )
                
                print(f"✅ Created test user: {username}")
            else:
                print(f"ℹ️ Test user already exists: {username}")
    
    def create_demo_cargo(self):
        """Create demo cargo for testing"""
        if Cargo.objects.count() < 3:
            demo_shipper = User.objects.filter(username='demo_shipper').first()
            demo_carrier = User.objects.filter(username='demo_carrier').first()
            
            if demo_shipper:
                demo_cargos = [
                    {
                        'pickup_address': 'Knez Mihailova 1, Beograd',
                        'pickup_lat': 44.8176,
                        'pickup_lng': 20.4633,
                        'delivery_address': 'Novi Sad Centar',
                        'delivery_lat': 45.2671,
                        'delivery_lng': 19.8335,
                        'pallet_count': 5,
                        'weight': 500.0,
                        'description': 'Demo pošiljka - elektronska oprema',
                        'price': 15000,
                        'distance_km': 95.2,
                        'status': 'pending_carrier'
                    },
                    {
                        'pickup_address': 'Terazije 5, Beograd',
                        'pickup_lat': 44.8125,
                        'pickup_lng': 20.4612,
                        'delivery_address': 'Niš Centar',
                        'delivery_lat': 43.3209,
                        'delivery_lng': 21.8958,
                        'pallet_count': 3,
                        'weight': 300.0,
                        'description': 'Demo pošiljka - tekstil',
                        'price': 18000,
                        'distance_km': 237.5,
                        'status': 'pending_carrier'
                    }
                ]
                
                for cargo_data in demo_cargos:
                    if not Cargo.objects.filter(
                        pickup_address=cargo_data['pickup_address'],
                        delivery_address=cargo_data['delivery_address']
                    ).exists():
                        Cargo.objects.create(
                            shipper=demo_shipper,
                            **cargo_data
                        )
                        print(f"✅ Created demo cargo: {cargo_data['pickup_address']} → {cargo_data['delivery_address']}")
    
    def start_django_server(self):
        """Start Django development server"""
        print("🚀 Starting Django server...")
        
        # Run migrations first
        print("📊 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Start server in background
        self.django_process = subprocess.Popen([
            sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
        ], cwd=project_dir)
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:8000/', timeout=5)
            print("✅ Django server is running on http://localhost:8000/")
            return True
        except requests.exceptions.RequestException:
            print("❌ Failed to start Django server")
            return False
    
    def start_ngrok_tunnel(self):
        """Start ngrok tunnel"""
        print("🌐 Starting ngrok tunnel...")
        
        try:
            # Start ngrok
            self.ngrok_process = subprocess.Popen([
                'ngrok', 'http', '8000', '--log=stdout'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for ngrok to start
            time.sleep(3)
            
            # Get public URL from ngrok API
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=10)
                if response.status_code == 200:
                    tunnels = response.json()['tunnels']
                    if tunnels:
                        self.public_url = tunnels[0]['public_url']
                        print(f"✅ Ngrok tunnel active: {self.public_url}")
                        return True
                    else:
                        print("❌ No active tunnels found")
                        return False
                else:
                    print(f"❌ Failed to get tunnel info: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to connect to ngrok API: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start ngrok: {e}")
            return False
    
    def display_test_info(self):
        """Display test mode information"""
        print("\n" + "="*60)
        print("🎯 TOVAR TAXI - TEST MODE ACTIVE")
        print("="*60)
        print(f"🌐 Public URL: {self.public_url}")
        print(f"🏠 Local URL: http://localhost:8000/")
        print("\n📋 Test Accounts:")
        print("   👤 Naručilac: demo_shipper / demo123")
        print("   🚛 Prevoznik: demo_carrier / demo123") 
        print("   👨‍💼 Admin: demo_admin / demo123")
        print("\n🔗 Quick Links:")
        print(f"   📦 Cargo Map: {self.public_url}/transport/cargo-map/")
        print(f"   📋 Cargo List: {self.public_url}/transport/cargo-list/")
        print(f"   👨‍💼 Admin: {self.public_url}/admin/")
        print("\n⚠️  TEST MODE FEATURES:")
        print("   • Demo data pre-loaded")
        print("   • Stripe in test mode (use test cards)")
        print("   • No real payments processed")
        print("   • External access via ngrok")
        print("\n💳 Stripe Test Cards:")
        print("   • Success: 4242424242424242")
        print("   • Decline: 4000000000000002")
        print("   • Any future date, any CVC")
        print("\n🛑 Press Ctrl+C to stop test mode")
        print("="*60)
    
    def cleanup(self):
        """Cleanup processes"""
        print("\n🛑 Stopping test mode...")
        
        if self.ngrok_process:
            self.ngrok_process.terminate()
            print("✅ Ngrok tunnel stopped")
        
        if self.django_process:
            self.django_process.terminate()
            print("✅ Django server stopped")
        
        print("✅ Test mode cleanup complete")
    
    def run(self):
        """Main test mode runner"""
        try:
            print("🚀 TOVAR TAXI - TEST MODE SETUP")
            print("="*40)
            
            # Check prerequisites
            if not self.check_ngrok_installed():
                return False
            
            # Setup test environment
            self.setup_test_environment()
            
            # Start Django server
            if not self.start_django_server():
                return False
            
            # Start ngrok tunnel
            if not self.start_ngrok_tunnel():
                self.cleanup()
                return False
            
            # Display info and wait
            self.display_test_info()
            self.test_mode_active = True
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            return True
            
        except Exception as e:
            print(f"❌ Error in test mode: {e}")
            return False
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    test_mode = NgrokTestMode()
    success = test_mode.run()
    
    if success:
        print("✅ Test mode completed successfully")
    else:
        print("❌ Test mode failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
