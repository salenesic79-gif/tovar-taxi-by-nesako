# Uputstvo za Programera: Implementacija Tovar Taxi Aplikacije

## Pregled Projekta

Tovar Taxi je Django web aplikacija namenjena optimizaciji transporta paleta kao dodatak postojećim turama prevoznika. Aplikacija omogućava pošiljaocima da unose teret, dobijaju predlog eko-ambalaže, vide mapu sa rutom, i plaćaju preko Stripe-a u CarGo stilu (rezervacija sredstava unapred, isplata prevozniku nakon istovara).

## Tehnički Stack

- **Backend**: Python 3.x, Django 4.x
- **Frontend**: Bootstrap 5, JavaScript, Leaflet.js
- **Baza podataka**: SQLite (development), PostgreSQL sa PostGIS (production)
- **Plaćanje**: Stripe API (test i live mode)
- **Mape**: Leaflet.js sa OpenStreetMap
- **Geolokacija**: geopy biblioteka
- **Notifikacije**: Django Channels ili Service Workers
- **Audio**: HTML5 Audio API

## Struktura Projekta

```
tovar_taxi/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── tovar_taxi/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── eco_app/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   └── tests.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── map.html
│   └── confirm.html
├── static/
│   ├── css/
│   ├── js/
│   └── audio/
│       ├── ping.mp3
│       ├── success.wav
│       └── alert.ogg
└── media/
```

## Requirements.txt

```
Django==4.2.7
geopy==2.4.0
stripe==7.8.0
python-decouple==3.8
django-bootstrap5==23.3
django-channels==4.0.0
psycopg2-binary==2.9.9
django-bleach==3.0.0
```

## Modeli (eco_app/models.py)

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    ROLE_CHOICES = [
        ('shipper', 'Pošiljalac'),
        ('carrier', 'Prevoznik'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    stripe_account_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Cargo(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('reserved', 'Rezervisano'),
        ('paid', 'Plaćeno'),
        ('delivered', 'Isporučeno'),
    ]
    
    shipper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    carrier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    
    # Teret info
    weight = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.1)])
    pallet_count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Lokacije
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_address = models.CharField(max_length=255)
    
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    delivery_address = models.CharField(max_length=255)
    
    # Cene i plaćanje
    distance_km = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # Eko-ambalaža
    eco_packaging = models.TextField(blank=True)
    
    # Status i vreme
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    message = models.TextField()
    sound_file = models.CharField(max_length=50, default='ping.mp3')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Tabela Cena

```python
# eco_app/utils.py
def calculate_price(pallet_count, distance_km):
    """Izračunava cenu na osnovu broja paleta i udaljenosti"""
    
    if distance_km <= 200:
        prices_under_200 = {
            1: 4000,
            2: 6400,
            3: 8400,
            4: 10000,
            5: 12000
        }
        return prices_under_200.get(pallet_count, 0)
    else:
        prices_over_200 = {
            1: 5500,
            2: 9000,
            3: 11850,
            4: 14200,
            5: 17000
        }
        return prices_over_200.get(pallet_count, 0)

def get_eco_packaging_suggestion(weight):
    """Predlaže eko-ambalažu na osnovu težine"""
    
    if weight <= 5:
        return "Biorazgradiva mala kutija (do 5kg) - preporučujemo kartonsku ambalažu od recikliranog materijala"
    elif weight <= 20:
        return "Srednja reciklirana kutija (5-20kg) - koristi ojačanu kartonsku ambalažu sa zaštitnim materijalom"
    else:
        return "Velika kutija sa zaštitom (>20kg) - koristi drvenu paletu sa biorazgradivom folijom za zaštitu"
```

## Views (eco_app/views.py)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from geopy.distance import geodesic
import stripe
import json
from .models import Cargo, Notification, Profile
from .utils import calculate_price, get_eco_packaging_suggestion

# Stripe konfiguracija
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def dashboard(request):
    """Glavni dashboard sa listom tereta"""
    if request.user.profile.role == 'shipper':
        cargos = Cargo.objects.filter(shipper=request.user).order_by('-created_at')
    else:
        cargos = Cargo.objects.filter(carrier=request.user).order_by('-created_at')
    
    return render(request, 'dashboard.html', {'cargos': cargos})

@login_required
def cargo_map(request):
    """Stranica sa mapom za kreiranje nove rezervacije"""
    if request.method == 'POST':
        try:
            # Uzmi podatke iz forme
            weight = float(request.POST.get('weight'))
            pallet_count = int(request.POST.get('pallet_count'))
            pickup_lat = float(request.POST.get('pickup_lat'))
            pickup_lon = float(request.POST.get('pickup_lon'))
            pickup_address = request.POST.get('pickup_address')
            delivery_lat = float(request.POST.get('delivery_lat'))
            delivery_lon = float(request.POST.get('delivery_lon'))
            delivery_address = request.POST.get('delivery_address')
            
            # Izračunaj udaljenost
            pickup_coords = (pickup_lat, pickup_lon)
            delivery_coords = (delivery_lat, delivery_lon)
            distance = geodesic(pickup_coords, delivery_coords).kilometers
            
            # Izračunaj cenu
            price = calculate_price(pallet_count, distance)
            
            # Predlog eko-ambalaže
            eco_packaging = get_eco_packaging_suggestion(weight)
            
            # Kreiraj Stripe PaymentIntent (rezervacija)
            intent = stripe.PaymentIntent.create(
                amount=int(price * 100),  # u centima
                currency='rsd',
                capture_method='manual',  # rezervacija bez naplate
                metadata={
                    'shipper_id': request.user.id,
                    'pallet_count': pallet_count,
                    'distance': distance
                }
            )
            
            # Sačuvaj cargo objekat
            cargo = Cargo.objects.create(
                shipper=request.user,
                weight=weight,
                pallet_count=pallet_count,
                pickup_latitude=pickup_lat,
                pickup_longitude=pickup_lon,
                pickup_address=pickup_address,
                delivery_latitude=delivery_lat,
                delivery_longitude=delivery_lon,
                delivery_address=delivery_address,
                distance_km=distance,
                price=price,
                payment_intent_id=intent.id,
                eco_packaging=eco_packaging,
                status='reserved'
            )
            
            # Kreiraj notifikaciju
            Notification.objects.create(
                user=request.user,
                cargo=cargo,
                message=f"Nova rezervacija kreirana - {pallet_count} paleta, {distance:.1f}km, {price} RSD",
                sound_file='ping.mp3'
            )
            
            return JsonResponse({
                'success': True,
                'cargo_id': cargo.id,
                'client_secret': intent.client_secret,
                'price': price,
                'distance': distance,
                'eco_packaging': eco_packaging
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'map.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def confirm_delivery(request, cargo_id):
    """Potvrda istovara i isplata prevozniku"""
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    # Proveri da li je korisnik prevoznik za ovaj teret
    if request.user.profile.role != 'carrier' or cargo.carrier != request.user:
        messages.error(request, 'Nemate dozvolu za ovu akciju.')
        return redirect('dashboard')
    
    if request.method == 'POST' and cargo.status == 'reserved':
        try:
            # Izvrši Stripe capture (isplata)
            stripe.PaymentIntent.capture(cargo.payment_intent_id)
            
            # Ažuriraj status
            cargo.status = 'paid'
            cargo.delivered_at = timezone.now()
            cargo.save()
            
            # Notifikacija za pošiljaoce
            Notification.objects.create(
                user=cargo.shipper,
                cargo=cargo,
                message=f"Teret isporučen i plaćanje potvrđeno - {cargo.price} RSD",
                sound_file='success.wav'
            )
            
            # Notifikacija za prevoznika
            Notification.objects.create(
                user=request.user,
                cargo=cargo,
                message=f"Isplata potvrđena - {cargo.price} RSD",
                sound_file='success.wav'
            )
            
            messages.success(request, 'Istovar potvrđen i isplata izvršena!')
            
        except Exception as e:
            messages.error(request, f'Greška pri potvrdi: {str(e)}')
    
    return render(request, 'confirm.html', {'cargo': cargo})

def notifications_api(request):
    """API za dobijanje notifikacija"""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).order_by('-created_at')[:5]
        
        data = [{
            'id': n.id,
            'message': n.message,
            'sound_file': n.sound_file,
            'created_at': n.created_at.isoformat()
        } for n in notifications]
        
        return JsonResponse({'notifications': data})
    
    return JsonResponse({'notifications': []})
```

## Templates

### base.html
```html
<!DOCTYPE html>
<html lang="sr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Tovar Taxi{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <!-- FontAwesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        /* Responsive Design */
        @media (max-width: 768px) {
            .main-content {
                min-height: 60vh !important;
                width: 80% !important;
            }
            
            .notification-popup {
                position: fixed !important;
                top: 20% !important;
                left: 10% !important;
                width: 80% !important;
                height: 60% !important;
                z-index: 9999 !important;
            }
        }
        
        @media (min-width: 769px) {
            .notification-popup {
                position: fixed !important;
                top: 0 !important;
                right: 0 !important;
                width: 25% !important;
                height: 25% !important;
                z-index: 9999 !important;
            }
        }
        
        .notification-popup {
            background: rgba(0, 123, 255, 0.95);
            color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            display: none;
        }
        
        .map-container {
            height: 400px;
            width: 100%;
        }
        
        @media (max-width: 768px) {
            .map-container {
                height: 60vh;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">
                <i class="fas fa-truck"></i> Tovar Taxi
            </a>
            
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'dashboard' %}">Dashboard</a>
                    <a class="nav-link" href="{% url 'cargo_map' %}">Nova Rezervacija</a>
                    <a class="nav-link" href="{% url 'logout' %}">Odjava</a>
                {% else %}
                    <a class="nav-link" href="{% url 'login' %}">Prijava</a>
                    <a class="nav-link" href="{% url 'register' %}">Registracija</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mt-4 main-content">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>

    <!-- Notification Popup -->
    <div id="notificationPopup" class="notification-popup">
        <h5 id="notificationTitle">Notifikacija</h5>
        <p id="notificationMessage"></p>
        <button class="btn btn-light btn-sm" onclick="closeNotification()">Zatvori</button>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://js.stripe.com/v3/"></script>
    
    <script>
        // Notification System
        function showNotification(message, soundFile = 'ping.mp3') {
            document.getElementById('notificationMessage').textContent = message;
            document.getElementById('notificationPopup').style.display = 'block';
            
            // Play sound
            const audio = new Audio(`/static/audio/${soundFile}`);
            audio.play().catch(e => console.log('Audio play failed:', e));
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                closeNotification();
            }, 5000);
        }
        
        function closeNotification() {
            document.getElementById('notificationPopup').style.display = 'none';
        }
        
        // Poll for notifications every 10 seconds
        if ({{ user.is_authenticated|yesno:"true,false" }}) {
            setInterval(() => {
                fetch('/api/notifications/')
                    .then(response => response.json())
                    .then(data => {
                        data.notifications.forEach(notification => {
                            showNotification(notification.message, notification.sound_file);
                        });
                    })
                    .catch(e => console.log('Notification fetch failed:', e));
            }, 10000);
        }
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### map.html
```html
{% extends 'base.html' %}

{% block title %}Nova Rezervacija - Tovar Taxi{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <h2>Nova Rezervacija Tereta</h2>
        
        <!-- Mapa -->
        <div id="map" class="map-container mb-4"></div>
        
        <!-- Forma -->
        <form id="cargoForm">
            {% csrf_token %}
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="weight" class="form-label">Težina (kg)</label>
                        <input type="number" class="form-control" id="weight" name="weight" step="0.1" min="0.1" required>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="pallet_count" class="form-label">Broj paleta</label>
                        <select class="form-select" id="pallet_count" name="pallet_count" required>
                            <option value="">Izaberite...</option>
                            <option value="1">1 paleta</option>
                            <option value="2">2 palete</option>
                            <option value="3">3 palete</option>
                            <option value="4">4 palete</option>
                            <option value="5">5 paleta</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="pickup_address" class="form-label">Adresa preuzimanja</label>
                        <input type="text" class="form-control" id="pickup_address" name="pickup_address" required>
                        <input type="hidden" id="pickup_lat" name="pickup_lat">
                        <input type="hidden" id="pickup_lon" name="pickup_lon">
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="mb-3">
                        <label for="delivery_address" class="form-label">Adresa dostave</label>
                        <input type="text" class="form-control" id="delivery_address" name="delivery_address" required>
                        <input type="hidden" id="delivery_lat" name="delivery_lat">
                        <input type="hidden" id="delivery_lon" name="delivery_lon">
                    </div>
                </div>
            </div>
            
            <!-- Stripe Card Element -->
            <div class="mb-3">
                <label class="form-label">Kartica za plaćanje</label>
                <div id="card-element" class="form-control" style="height: 40px; padding: 10px;"></div>
                <div id="card-errors" role="alert" class="text-danger mt-2"></div>
            </div>
            
            <button type="submit" class="btn btn-primary btn-lg">
                <i class="fas fa-truck"></i> Kreiraj Rezervaciju
            </button>
        </form>
    </div>
    
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h5>Tabela Cena</h5>
            </div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Palete</th>
                            <th>≤200km</th>
                            <th>>200km</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>1</td><td>4.000</td><td>5.500</td></tr>
                        <tr><td>2</td><td>6.400</td><td>9.000</td></tr>
                        <tr><td>3</td><td>8.400</td><td>11.850</td></tr>
                        <tr><td>4</td><td>10.000</td><td>14.200</td></tr>
                        <tr><td>5</td><td>12.000</td><td>17.000</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div id="calculationResult" class="card mt-3" style="display: none;">
            <div class="card-header">
                <h5>Rezultat Kalkulacije</h5>
            </div>
            <div class="card-body">
                <p><strong>Udaljenost:</strong> <span id="resultDistance"></span> km</p>
                <p><strong>Cena:</strong> <span id="resultPrice"></span> RSD</p>
                <div id="ecoPackaging" class="alert alert-info"></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Inicijalizuj mapu
    const map = L.map('map').setView([44.8176, 20.4633], 10); // Beograd centar
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    let pickupMarker, deliveryMarker, routeLine;
    
    // Stripe inicijalizacija
    const stripe = Stripe('{{ stripe_public_key }}');
    const elements = stripe.elements();
    const cardElement = elements.create('card');
    cardElement.mount('#card-element');
    
    // Geocoding funkcija (simulacija - u produkciji koristi pravi API)
    function geocodeAddress(address, callback) {
        // Simulacija geocoding-a - u produkciji koristi Nominatim ili Google API
        const coords = {
            'Beograd': [44.8176, 20.4633],
            'Novi Sad': [45.2671, 19.8335],
            'Niš': [43.3209, 21.8958]
        };
        
        const found = Object.keys(coords).find(city => 
            address.toLowerCase().includes(city.toLowerCase())
        );
        
        if (found) {
            callback(coords[found]);
        } else {
            // Default Beograd
            callback([44.8176, 20.4633]);
        }
    }
    
    // Event listeneri za adrese
    document.getElementById('pickup_address').addEventListener('blur', function() {
        const address = this.value;
        if (address) {
            geocodeAddress(address, function(coords) {
                document.getElementById('pickup_lat').value = coords[0];
                document.getElementById('pickup_lon').value = coords[1];
                
                if (pickupMarker) map.removeLayer(pickupMarker);
                pickupMarker = L.marker(coords).addTo(map)
                    .bindPopup('Preuzimanje: ' + address);
                
                updateRoute();
            });
        }
    });
    
    document.getElementById('delivery_address').addEventListener('blur', function() {
        const address = this.value;
        if (address) {
            geocodeAddress(address, function(coords) {
                document.getElementById('delivery_lat').value = coords[0];
                document.getElementById('delivery_lon').value = coords[1];
                
                if (deliveryMarker) map.removeLayer(deliveryMarker);
                deliveryMarker = L.marker(coords).addTo(map)
                    .bindPopup('Dostava: ' + address);
                
                updateRoute();
            });
        }
    });
    
    function updateRoute() {
        if (pickupMarker && deliveryMarker) {
            if (routeLine) map.removeLayer(routeLine);
            
            const pickupCoords = pickupMarker.getLatLng();
            const deliveryCoords = deliveryMarker.getLatLng();
            
            routeLine = L.polyline([
                [pickupCoords.lat, pickupCoords.lng],
                [deliveryCoords.lat, deliveryCoords.lng]
            ], {color: 'blue', weight: 3}).addTo(map);
            
            map.fitBounds(routeLine.getBounds(), {padding: [20, 20]});
        }
    }
    
    // Submit forma
    document.getElementById('cargoForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        try {
            // Prvo pošalji podatke za kalkulaciju
            const response = await fetch('{% url "cargo_map" %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Prikaži rezultat
                document.getElementById('resultDistance').textContent = result.distance.toFixed(1);
                document.getElementById('resultPrice').textContent = result.price.toLocaleString();
                document.getElementById('ecoPackaging').innerHTML = result.eco_packaging;
                document.getElementById('calculationResult').style.display = 'block';
                
                // Potvrdi plaćanje
                const {error} = await stripe.confirmCardPayment(result.client_secret, {
                    payment_method: {
                        card: cardElement,
                    }
                });
                
                if (error) {
                    showNotification('Greška pri plaćanju: ' + error.message, 'alert.ogg');
                } else {
                    showNotification('Rezervacija uspešno kreirana!', 'ping.mp3');
                    setTimeout(() => {
                        window.location.href = '{% url "dashboard" %}';
                    }, 2000);
                }
            } else {
                showNotification('Greška: ' + result.error, 'alert.ogg');
            }
        } catch (error) {
            showNotification('Greška pri kreiranju rezervacije', 'alert.ogg');
        }
    });
</script>
{% endblock %}
```

## Audio Fajlovi

Kreiraj folder `static/audio/` i dodaj sledeće zvukove:

1. **ping.mp3** - Za nove rezervacije (kratki "ping" zvuk)
2. **success.wav** - Za uspešne isplate (pozitivan zvuk)
3. **alert.ogg** - Za greške (upozoravajući zvuk)

Možeš ih preuzeti sa:
- freesound.org
- zapsplat.com (besplatni nalozi)
- Ili koristi jednostavne tone generatore online

## Test Mode i Ngrok Setup

```python
# settings.py
import os
from decouple import config

DEBUG = config('DEBUG', default=True, cast=bool)
TEST_MODE = config('TEST_MODE', default=False, cast=bool)

# Stripe keys
if TEST_MODE:
    STRIPE_PUBLIC_KEY = config('STRIPE_TEST_PUBLIC_KEY')
    STRIPE_SECRET_KEY = config('STRIPE_TEST_SECRET_KEY')
else:
    STRIPE_PUBLIC_KEY = config('STRIPE_LIVE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = config('STRIPE_LIVE_SECRET_KEY')

# Ngrok setup za test mode
if TEST_MODE and DEBUG:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = ['https://*.ngrok.io']
```

```bash
# Instalacija Ngrok-a
# 1. Preuzmi sa https://ngrok.com/
# 2. Registruj se i dobij authtoken
# 3. Pokreni:
ngrok authtoken YOUR_AUTHTOKEN
ngrok http 8000

# Aplikacija će biti dostupna na https://random-string.ngrok.io
```

## Deployment Checklist

### Pre produkcije:
1. **Promeni Stripe ključeve** na live verzije u .env
2. **Postavi PostgreSQL** sa PostGIS ekstenzijom
3. **Konfiguriši ALLOWED_HOSTS** u settings.py
4. **Dodaj SSL sertifikat** (Let's Encrypt)
5. **Testiraj sve funkcionalnosti** end-to-end

### Test Scenario:
1. Registruj se kao pošiljalac
2. Kreiraj novu rezervaciju sa test karticom (4242 4242 4242 4242)
3. Proveri da li je PaymentIntent kreiran u Stripe dashboard-u
4. Registruj se kao prevoznik
5. Potvrdi istovar
6. Proveri da li je capture izvršen u Stripe-u

### Sigurnosni zahtevi:
- Koristi HTTPS u produkciji
- Validiraj sve inpute na backend-u
- Implementiraj rate limiting
- Dodaj logging za sve transakcije
- Koristi Django security middleware

Aplikacija je sada spremna za implementaciju sa svim potrebnim funkcionalnostima: GPS mape, sistem naplate, notifikacije sa zvukovima, responsive dizajn, i test mode za pregled sa drugih uređaja.
