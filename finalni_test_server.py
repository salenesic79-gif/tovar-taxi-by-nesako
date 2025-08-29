#!/usr/bin/env python
"""
Finalni test skripta za Tovar Taxi server
Objašnjenje: Proverava da li Django server radi i prikazuje IP adresu za pristup sa drugih uređaja
"""

import os
import sys
import socket
import subprocess
import time
import requests
from datetime import datetime

def get_local_ip():
    """Dobija lokalnu IP adresu računara"""
    try:
        # Kreiranje socket konekcije ka Google DNS-u da dobijemo lokalnu IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def check_server_running(ip, port=8000):
    """Proverava da li server radi na određenoj IP adresi i portu"""
    try:
        response = requests.get(f"http://{ip}:{port}", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚛 TOVAR TAXI - FINALNI TEST SERVERA")
    print("=" * 50)
    
    # Dobijanje IP adrese
    local_ip = get_local_ip()
    print(f"📍 Lokalna IP adresa: {local_ip}")
    
    # Proverava da li server radi na localhost
    if check_server_running("127.0.0.1"):
        print("✅ Server radi na localhost:8000")
    else:
        print("❌ Server NE radi na localhost:8000")
    
    # Proverava da li server radi na lokalnoj IP adresi
    if check_server_running(local_ip):
        print(f"✅ Server radi na {local_ip}:8000")
        print(f"🌐 Pristup sa drugih uređaja: http://{local_ip}:8000")
    else:
        print(f"❌ Server NE radi na {local_ip}:8000")
        print("🔧 Pokušavam da pokrenemo server...")
        
        # Pokušaj pokretanja servera
        os.chdir(r"c:\Users\PC\Desktop\tovar-taxi-by-nesako")
        try:
            subprocess.Popen([sys.executable, "manage.py", "runserver", f"0.0.0.0:8000"])
            print("🚀 Server je pokrennut!")
            time.sleep(3)
            
            if check_server_running(local_ip):
                print(f"✅ Server sada radi na {local_ip}:8000")
            else:
                print("❌ Server se nije pokrenuo uspešno")
        except Exception as e:
            print(f"❌ Greška pri pokretanju servera: {e}")
    
    print("\n📱 TEST NALOZI:")
    print("👤 Admin: admin / admin123")
    print("📦 Naručilac: narucilac / test123")
    print("🚛 Prevoznik: prevoznik / test123")
    
    print(f"\n⏰ Test završen: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
