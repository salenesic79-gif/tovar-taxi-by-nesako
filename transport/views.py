from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
import json
import math

from .models import (
    Profile, Vehicle, Shipment, ShipmentOffer, Tour, ChatMessage, Notification, Location,
    InstantDelivery, FoodDelivery, PaymentReservation, DriverLocation, PremiumSubscription, Cargo, CenaPoKilometrazi
)
from .forms import SignupForm, ShipmentForm, VehicleForm, ShipmentOfferForm, TourForm




def home_view(request):
    """Glavna stranica aplikacije - redirect authenticated users to their dashboard"""
    # Ako je korisnik ulogovan, preusmeri ga na odgovarajući dashboard
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.role == 'naručilac':
                return redirect('transport:shipper_dashboard')
            elif profile.role == 'prevoznik':
                return redirect('transport:carrier_dashboard')
            elif profile.role == 'vozač':
                return redirect('transport:carrier_dashboard')
        except Profile.DoesNotExist:
            pass  # Nastavi sa prikazom home stranice
    
    # Pojednostavljena verzija za smanjenje opterećenja baze
    context = {
        'total_shipments': 0,
        'total_carriers': 0,
        'total_vehicles': 0,
    }
    return render(request, 'transport/home.html', context)


@login_required
def shipper_dashboard(request):
    """Dashboard za naručioce"""
    if request.user.profile.role != 'naručilac':
        return redirect('home')
    
    shipments = Shipment.objects.filter(sender=request.user).order_by('-created_at')
    recent_shipments = shipments[:5]
    
    context = {
        'shipments': recent_shipments,
        'total_shipments': shipments.count(),
        'active_shipments': shipments.filter(status__in=['published', 'in_progress']).count(),
        'completed_shipments': shipments.filter(status='completed').count(),
    }
    return render(request, 'transport/shipper_dashboard.html', context)


@login_required
def carrier_dashboard(request):
    """Dashboard za prevoznike"""
    try:
        profile = request.user.profile
        if profile.role not in ['prevoznik', 'vozač']:
            return redirect('home')
    except Profile.DoesNotExist:
        # Kreirati profil za prevoznika ako ne postoji
        Profile.objects.create(
            user=request.user,
            role='prevoznik',
            phone_number='',
            address='',
            company_name=''
        )
    
    vehicles = Vehicle.objects.filter(owner=request.user)
    offers = ShipmentOffer.objects.filter(carrier=request.user).order_by('-created_at')
    tours = Tour.objects.filter(driver=request.user).order_by('-created_at')
    
    context = {
        'vehicles': vehicles,
        'total_vehicles': vehicles.count(),
        'available_vehicles': vehicles.filter(is_available=True).count(),
        'offers': offers[:5],
        'tours': tours[:5],
        'total_offers': offers.count(),
        'accepted_offers': offers.filter(status='accepted').count(),
    }
    return render(request, 'transport/carrier_dashboard.html', context)




@login_required
def create_shipment(request):
    """Kreiranje nove pošiljke"""
    if request.user.profile.role != 'naručilac':
        return redirect('home')
    
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.sender = request.user
            shipment.save()
            messages.success(request, 'Pošiljka je uspešno kreirana!')
            return redirect('shipment_detail', pk=shipment.pk)
    else:
        form = ShipmentForm()
    
    return render(request, 'transport/create_shipment.html', {'form': form})


@login_required
def shipment_detail(request, pk):
    """Detalji pošiljke"""
    shipment = get_object_or_404(Shipment, pk=pk)
    offers = shipment.offers.all().order_by('-created_at')
    
    # Proveri da li korisnik može da vidi pošiljku
    can_view = (
        shipment.sender == request.user or
        request.user.profile.role == 'prevoznik' or
        request.user.is_staff
    )
    
    if not can_view:
        messages.error(request, 'Nemate dozvolu da vidite ovu pošiljku.')
        return redirect('home')
    
    context = {
        'shipment': shipment,
        'offers': offers,
        'can_make_offer': request.user.profile.role in ['prevoznik', 'vozač'] and shipment.status == 'published',
        'is_owner': shipment.sender == request.user,
    }
    return render(request, 'transport/shipment_detail.html', context)


@login_required
def make_offer(request, shipment_id):
    """Kreiranje ponude za pošiljku"""
    if request.user.profile.role != 'prevoznik':
        return redirect('home')
    
    shipment = get_object_or_404(Shipment, pk=shipment_id, status='published')
    
    # Proveri da li već postoji ponuda od ovog prevoznika
    existing_offer = ShipmentOffer.objects.filter(
        shipment=shipment, 
        carrier=request.user
    ).first()
    
    if existing_offer:
        messages.warning(request, 'Već ste poslali ponudu za ovu pošiljku.')
        return redirect('shipment_detail', pk=shipment_id)
    
    if request.method == 'POST':
        form = ShipmentOfferForm(request.POST, user=request.user)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.shipment = shipment
            offer.carrier = request.user
            offer.save()
            
            # Kreiraj notifikaciju za naručioca
            Notification.objects.create(
                user=shipment.sender,
                notification_type='new_offer',
                title='Nova ponuda',
                message=f'Dobili ste novu ponudu za pošiljku "{shipment.title}"',
                shipment=shipment
            )
            
            messages.success(request, 'Ponuda je uspešno poslata!')
            return redirect('shipment_detail', pk=shipment_id)
    else:
        form = ShipmentOfferForm(user=request.user)
    
    context = {
        'form': form,
        'shipment': shipment,
    }
    return render(request, 'transport/make_offer.html', context)


@login_required
def freight_exchange(request):
    """Berza tereta - lista dostupnih pošiljki"""
    # Prikaži samo neprihvaćene aktivne ponude, sortirane po mestu preuzimanja
    shipments = Shipment.objects.filter(
        status='published'
    ).exclude(
        shipmentoffer__status='accepted'
    ).order_by('pickup_city', 'pickup_region', 'delivery_city')
    
    # Filtriranje
    pickup_city = request.GET.get('pickup_city')
    delivery_city = request.GET.get('delivery_city')
    cargo_type = request.GET.get('cargo_type')
    max_weight = request.GET.get('max_weight')
    min_price = request.GET.get('min_price')
    pickup_date = request.GET.get('pickup_date')
    
    if pickup_city:
        shipments = shipments.filter(pickup_city__icontains=pickup_city)
    if delivery_city:
        shipments = shipments.filter(delivery_city__icontains=delivery_city)
    if cargo_type:
        shipments = shipments.filter(cargo_type__icontains=cargo_type)
    if max_weight:
        try:
            shipments = shipments.filter(weight__lte=float(max_weight))
        except ValueError:
            pass
    if min_price:
        try:
            shipments = shipments.filter(offered_price__gte=float(min_price))
        except ValueError:
            pass
    if pickup_date:
        shipments = shipments.filter(pickup_date__date=pickup_date)
    
    # Dodaj gradove za filter dropdown
    from .models import City
    cities = City.objects.all().order_by('name')
    
    context = {
        'shipments': shipments,
        'cities': cities,
        'pickup_city': pickup_city,
        'delivery_city': delivery_city,
        'cargo_type': cargo_type,
        'last_updated': timezone.now(),
    }
    return render(request, 'transport/freight_exchange.html', context)


@login_required
def manage_vehicles(request):
    """Upravljanje vozilima"""
    if request.user.profile.role != 'prevoznik':
        return redirect('home')
    
    vehicles = Vehicle.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'vehicles': vehicles,
    }
    return render(request, 'transport/manage_vehicles.html', context)


@login_required
def add_vehicle(request):
    """Dodavanje novog vozila - AJAX compatible"""
    if request.user.profile.role != 'prevoznik':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Nemate dozvolu za dodavanje vozila'})
        return redirect('home')
    
    if request.method == 'POST':
        # Extract form data
        license_plate = request.POST.get('license_plate')
        vehicle_brand = request.POST.get('vehicle_brand')
        vehicle_color = request.POST.get('vehicle_color')
        transport_license = request.POST.get('transport_license')
        vehicle_type = request.POST.get('vehicle_type')
        loading_height = request.POST.get('loading_height')
        payload_capacity = request.POST.get('payload_capacity')
        
        # Validation
        errors = []
        if not license_plate:
            errors.append('Registarski broj je obavezan')
        if not vehicle_brand:
            errors.append('Marka vozila je obavezna')
        if not vehicle_color:
            errors.append('Boja vozila je obavezna')
        if not transport_license:
            errors.append('Broj dozvole za prevoz tereta je obavezan')
        if not vehicle_type:
            errors.append('Tip vozila je obavezan')
        if not loading_height:
            errors.append('Visina utovarnog dela je obavezna')
        if not payload_capacity:
            errors.append('Tovarna nosivost je obavezna')
            
        # Check if license plate already exists
        if Vehicle.objects.filter(license_plate=license_plate).exists():
            errors.append('Vozilo sa ovim registarskim brojem već postoji')
        
        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors})
            for error in errors:
                messages.error(request, error)
            return render(request, 'transport/add_vehicle.html')
        
        try:
            # Convert capacity from kg to tons
            capacity_tons = float(payload_capacity) / 1000
            
            # Create vehicle with correct field names
            vehicle = Vehicle.objects.create(
                owner=request.user,
                license_plate=license_plate,
                vehicle_brand=vehicle_brand,
                vehicle_color=vehicle_color,
                transport_license=transport_license,
                vehicle_type=vehicle_type,
                loading_height=int(loading_height),
                capacity=capacity_tons,
                volume=10.0,  # Default volume - can be calculated later
                is_available=True
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return vehicle data for dynamic addition to page
                vehicle_data = {
                    'license_plate': vehicle.license_plate,
                    'vehicle_brand': vehicle.vehicle_brand,
                    'vehicle_color': vehicle.vehicle_color,
                    'vehicle_type': vehicle.vehicle_type,
                    'capacity': vehicle.capacity,
                    'brand_code': '??'  # Simplified - brand code not needed
                }
                return JsonResponse({
                    'success': True, 
                    'message': 'Vozilo je uspešno dodato!',
                    'vehicle': vehicle_data
                })
            
            messages.success(request, 'Vozilo je uspešno dodato!')
            return redirect('transport:carrier_dashboard')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Greška pri dodavanju vozila: {str(e)}'})
            messages.error(request, f'Greška pri dodavanju vozila: {str(e)}')
    
    return render(request, 'transport/add_vehicle.html')




@login_required
def my_tours(request):
    """Lista tura korisnika"""
    if request.user.profile.role == 'prevoznik':
        tours = Tour.objects.filter(driver=request.user)
    elif request.user.profile.role == 'naručilac':
        tours = Tour.objects.filter(shipment__sender=request.user)
    else:
        tours = Tour.objects.none()
    
    tours = tours.order_by('-created_at')
    
    context = {
        'tours': tours,
    }
    return render(request, 'transport/my_tours.html', context)


@login_required
def tour_detail(request, pk):
    """Detalji ture"""
    tour = get_object_or_404(Tour, pk=pk)
    
    # Proveri dozvole
    can_view = (
        tour.driver == request.user or
        tour.shipment.sender == request.user or
        request.user.is_staff
    )
    
    if not can_view:
        messages.error(request, 'Nemate dozvolu da vidite ovu turu.')
        return redirect('home')
    
    chat_messages = ChatMessage.objects.filter(tour=tour).order_by('timestamp')
    
    context = {
        'tour': tour,
        'chat_messages': chat_messages,
        'can_chat': tour.driver == request.user or tour.shipment.sender == request.user,
    }
    return render(request, 'transport/tour_detail.html', context)


@login_required
def notifications(request):
    """Lista notifikacija"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Označi sve kao pročitane
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'transport/notifications.html', context)


@login_required
def create_shipment_request(request):
    """Kreiranje upita za prevoz robe - post-registration workflow za naručioce"""
    try:
        profile = request.user.profile
        if profile.role != 'naručilac':
            return redirect('home')
    except Profile.DoesNotExist:
        # Kreirati prazan profil za naručioca
        Profile.objects.create(
            user=request.user,
            role='naručilac',
            phone_number='',
            address='',
            company_name=''
        )
        messages.success(request, 'Profil je kreiran. Možete kreirati narudžbinu.')
    
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.sender = request.user
            shipment.save()
            messages.success(request, 'Upit za prevoz je uspešno kreiran!')
            return redirect('transport:shipper_dashboard')
    else:
        form = ShipmentForm()
    
    context = {
        'form': form,
        'title': 'Kreiraj upit za prevoz robe',
        'is_first_request': True
    }
    return render(request, 'transport/create_shipment_request.html', context)


@login_required
def create_route_availability(request):
    """Prijavljivanje rute sa slobodnim mestom - post-registration workflow za prevoznike"""
    try:
        profile = request.user.profile
        if profile.role not in ['prevoznik', 'vozač']:
            return redirect('home')
    except Profile.DoesNotExist:
        # Kreirati prazan profil za prevoznika
        Profile.objects.create(
            user=request.user,
            role='prevoznik',
            phone_number='',
            address='',
            company_name=''
        )
        messages.success(request, 'Profil je kreiran. Možete prijaviti rutu.')
    
    if request.method == 'POST':
        pickup_city = request.POST.get('pickup_city')
        delivery_city = request.POST.get('delivery_city')
        departure_date = request.POST.get('departure_date')
        available_capacity = request.POST.get('available_capacity')
        
        # Validacija
        errors = []
        
        if not pickup_city or not delivery_city or not departure_date:
            errors.append('Sva obavezna polja moraju biti popunjena.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'pickup_city': pickup_city,
                'delivery_city': delivery_city,
                'departure_date': departure_date,
                'available_capacity': available_capacity,
            }
            return render(request, 'transport/create_route_availability.html', context)
        
        # Kreiranje ili ažuriranje vozila sa dostupnošću
        vehicle, created = Vehicle.objects.get_or_create(
            owner=request.user,
            defaults={
                'vehicle_type': 'kamion',
                'license_plate': f"TEMP-{request.user.id}",
                'capacity': int(available_capacity) if available_capacity else 1000,
                'is_available': True
            }
        )
        
        if not created:
            vehicle.is_available = True
            vehicle.capacity = int(available_capacity) if available_capacity else vehicle.capacity
            vehicle.save()
        
        messages.success(request, 'Ruta sa slobodnim mestom je uspešno prijavljena!')
        return redirect('transport:carrier_dashboard')
    
    context = {
        'title': 'Prijavi rutu sa slobodnim mestom',
        'is_first_availability': True
    }
    return render(request, 'transport/create_route_availability.html', context)


# API Views
@login_required
@csrf_exempt
def accept_offer_api(request, offer_id):
    """API za prihvatanje ponude"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    offer = get_object_or_404(ShipmentOffer, pk=offer_id)
    
    if offer.shipment.sender != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if offer.status != 'pending':
        return JsonResponse({'error': 'Offer already processed'}, status=400)
    
    # Prihvati ponudu
    offer.status = 'accepted'
    offer.save()
    
    # Ažuriraj status pošiljke
    offer.shipment.status = 'in_progress'
    offer.shipment.save()
    
    # Odbij ostale ponude
    ShipmentOffer.objects.filter(
        shipment=offer.shipment
    ).exclude(pk=offer.pk).update(status='rejected')
    
    # Kreiraj turu
    tour = Tour.objects.create(
        shipment=offer.shipment,
        offer=offer,
        driver=offer.carrier,
        vehicle=offer.vehicle,
        status='confirmed'
    )
    
    # Kreiraj notifikacije
    Notification.objects.create(
        user=offer.carrier,
        notification_type='offer_accepted',
        title='Ponuda prihvaćena',
        message=f'Vaša ponuda za "{offer.shipment.title}" je prihvaćena!',
        shipment=offer.shipment,
        tour=tour
    )
    
    return JsonResponse({'success': True, 'tour_id': tour.pk})


@login_required
@csrf_exempt
def send_message_api(request, tour_id):
    """API za slanje poruke"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    tour = get_object_or_404(Tour, pk=tour_id)
    
    # Proveri dozvole
    if tour.driver != request.user and tour.shipment.sender != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        message = ChatMessage.objects.create(
            tour=tour,
            sender=request.user,
            message=message_text
        )
        
        # Kreiraj notifikaciju za drugog korisnika
        recipient = tour.shipment.sender if tour.driver == request.user else tour.driver
        Notification.objects.create(
            user=recipient,
            notification_type='new_message',
            title='Nova poruka',
            message=f'Dobili ste novu poruku u turi "{tour.shipment.title}"',
            tour=tour
        )
        
        return JsonResponse({
            'success': True,
            'message_id': message.pk,
            'timestamp': message.timestamp.isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@login_required
def websocket_test(request):
    """Test stranica za WebSocket funkcionalnost"""
    return render(request, 'transport/websocket_test.html')


def custom_login_view(request):
    """Custom login view sa role-based redirect"""
    # Očisti postojeće messages na početku GET zahteva
    if request.method == 'GET':
        storage = messages.get_messages(request)
        for message in storage:
            pass  # Ovo briše sve postojeće messages
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            messages.error(request, 'Molimo unesite korisničko ime i lozinku.')
            return render(request, 'registration/login.html')
        
        # Proveri da li korisnik postoji u bazi
        from django.db import models
        
        user_exists = User.objects.filter(
            models.Q(username__iexact=username) | 
            models.Q(email__iexact=username)
        ).exists()
        
        if not user_exists:
            messages.error(request, f'Korisnik "{username}" nije registrovan.')
            return render(request, 'registration/login.html')
        
        # Pokušaj autentifikaciju sa username
        user = authenticate(request, username=username, password=password)
        
        # Ako ne uspe sa username, pokušaj sa email (case insensitive)
        if user is None:
            try:
                user_by_email = User.objects.get(email__iexact=username)
                user = authenticate(request, username=user_by_email.username, password=password)
            except User.DoesNotExist:
                try:
                    user_by_username = User.objects.get(username__iexact=username)
                    user = authenticate(request, username=user_by_username.username, password=password)
                except User.DoesNotExist:
                    user = None
            
        if user is not None and user.is_active:
            login(request, user)
            
            # Proveri "Remember me" checkbox
            remember_me = request.POST.get('remember_me')
            if remember_me:
                # Postavi session da traje 30 dana
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 dana
            else:
                # Standardno ponašanje - session se briše kada se zatvori browser
                request.session.set_expiry(0)

            # Role-based redirect
            try:
                profile = user.profile

                if profile.role == 'naručilac':
                    return redirect('transport:shipper_dashboard')
                elif profile.role == 'prevoznik' or profile.role == 'vozač':
                    return redirect('transport:carrier_dashboard')
                else:
                    return redirect('home')
            except Profile.DoesNotExist:
                messages.error(request, 'Korisnik nema kreiran profil. Kontaktirajte administratora.')
                return render(request, 'registration/login.html')
        else:
            if user and not user.is_active:
                messages.error(request, 'Vaš nalog nije aktivan. Kontaktirajte administratora.')
            else:
                messages.error(request, 'Neispravna lozinka.')
    
    return render(request, 'registration/login.html')


# B2B i Instant Delivery Views

@login_required
def create_instant_delivery(request):
    """Kreiranje instant dostave - Uber/Glovo funkcionalnost"""
    if request.method == 'POST':
        pickup_address = request.POST.get('pickup_address')
        delivery_address = request.POST.get('delivery_address')
        delivery_type = request.POST.get('delivery_type')
        item_description = request.POST.get('item_description')
        estimated_weight = request.POST.get('estimated_weight')
        special_instructions = request.POST.get('special_instructions', '')
        
        # Kalkulacija cene na osnovu distance i tipa dostave
        base_price = 300.00
        if delivery_type == 'express':
            delivery_fee = 500.00
        elif delivery_type == 'same_day':
            delivery_fee = 300.00
        else:
            delivery_fee = 200.00
        
        total_price = base_price + delivery_fee
        
        # Kreiranje instant dostave
        delivery = InstantDelivery.objects.create(
            sender=request.user,
            pickup_address=pickup_address,
            delivery_address=delivery_address,
            delivery_type=delivery_type,
            item_description=item_description,
            estimated_weight=estimated_weight,
            special_instructions=special_instructions,
            price=total_price,
            delivery_fee=delivery_fee,
            estimated_delivery=timezone.now() + timezone.timedelta(hours=1)
        )
        
        # Kreiranje rezervacije plaćanja
        PaymentReservation.objects.create(
            shipment=None,
            amount=total_price,
            transaction_id=f"ID-{delivery.id}-{timezone.now().timestamp()}"
        )
        
        messages.success(request, 'Instant dostava je kreirana! Tražimo dostupnog vozača.')
        return redirect('transport:shipper_dashboard')
    
    context = {
        'title': 'Kreiraj instant dostavu',
        'delivery_types': InstantDelivery.DELIVERY_TYPE_CHOICES
    }
    return render(request, 'transport/create_instant_delivery.html', context)


@login_required
def create_food_delivery(request):
    """Kreiranje narudžbine hrane - Donesi funkcionalnost"""
    if request.method == 'POST':
        restaurant_name = request.POST.get('restaurant_name')
        restaurant_address = request.POST.get('restaurant_address')
        delivery_address = request.POST.get('delivery_address')
        customer_phone = request.POST.get('customer_phone')
        items_json = request.POST.get('items')
        total_amount = request.POST.get('total_amount')
        special_instructions = request.POST.get('special_instructions', '')
        
        try:
            items = json.loads(items_json) if items_json else []
        except json.JSONDecodeError:
            items = []
        
        # Kreiranje narudžbine hrane
        food_order = FoodDelivery.objects.create(
            customer=request.user,
            restaurant_name=restaurant_name,
            restaurant_address=restaurant_address,
            delivery_address=delivery_address,
            customer_phone=customer_phone,
            items=items,
            total_amount=total_amount,
            estimated_delivery=timezone.now() + timezone.timedelta(minutes=45)
        )
        
        # Kreiranje rezervacije plaćanja
        PaymentReservation.objects.create(
            shipment=None,
            amount=float(total_amount) + 200.00,
            transaction_id=f"FD-{food_order.id}-{timezone.now().timestamp()}"
        )
        
        messages.success(request, 'Narudžbina je poslata restoranu! Pratite status dostave.')
        return redirect('transport:shipper_dashboard')
    
    context = {
        'title': 'Naruči hranu'
    }
    return render(request, 'transport/create_food_delivery.html', context)


@login_required
def driver_dashboard_extended(request):
    """Prošireni dashboard za prevoznike sa instant i food delivery"""
    if request.user.profile.role != 'prevoznik':
        return redirect('home')
    
    # Dostupne instant dostave
    available_deliveries = InstantDelivery.objects.filter(
        status='pending',
        assigned_driver=None
    ).order_by('-created_at')[:10]
    
    # Dostupne food delivery
    available_food_orders = FoodDelivery.objects.filter(
        status__in=['confirmed', 'ready'],
        assigned_driver=None
    ).order_by('-ordered_at')[:10]
    
    # Trenutne dostave vozača
    active_deliveries = InstantDelivery.objects.filter(
        assigned_driver=request.user,
        status__in=['accepted', 'pickup', 'in_transit']
    )
    
    active_food_deliveries = FoodDelivery.objects.filter(
        assigned_driver=request.user,
        status__in=['pickup', 'ready']
    )
    
    context = {
        'available_deliveries': available_deliveries,
        'available_food_orders': available_food_orders,
        'active_deliveries': active_deliveries,
        'active_food_deliveries': active_food_deliveries,
    }
    return render(request, 'transport/carrier_dashboard.html', context)


@login_required
@csrf_exempt
def accept_delivery(request, delivery_id):
    """Prihvatanje instant dostave od strane vozača"""
    if request.method == 'POST':
        try:
            delivery = InstantDelivery.objects.get(id=delivery_id, status='pending')
            delivery.assigned_driver = request.user
            delivery.status = 'accepted'
            delivery.save()
            
            return JsonResponse({'success': True, 'message': 'Dostava je prihvaćena!'})
        except InstantDelivery.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Dostava nije pronađena.'})
    
    return JsonResponse({'success': False, 'message': 'Neispravna metoda.'})


@login_required
@csrf_exempt
def update_delivery_status(request, delivery_id):
    """Ažuriranje statusa dostave"""
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        try:
            delivery = InstantDelivery.objects.get(id=delivery_id, assigned_driver=request.user)
            delivery.status = new_status
            
            if new_status == 'pickup':
                delivery.pickup_time = timezone.now()
            elif new_status == 'delivered':
                delivery.delivery_time = timezone.now()
                # Naplaćivanje rezervisanih sredstava
                try:
                    payment = PaymentReservation.objects.get(
                        transaction_id__contains=f"ID-{delivery.id}"
                    )
                    payment.status = 'captured'
                    payment.captured_at = timezone.now()
                    payment.save()
                except PaymentReservation.DoesNotExist:
                    pass
            
            delivery.save()
            
            return JsonResponse({'success': True, 'message': f'Status ažuriran na {new_status}'})
        except InstantDelivery.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Dostava nije pronađena.'})
    
    return JsonResponse({'success': False, 'message': 'Neispravna metoda.'})


@login_required
@csrf_exempt
def update_location(request):
    """Ažuriranje GPS lokacije vozača"""
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        accuracy = request.POST.get('accuracy', 0.0)
        speed = request.POST.get('speed', 0.0)
        heading = request.POST.get('heading', 0.0)
        
        # Deaktiviranje prethodnih lokacija
        DriverLocation.objects.filter(driver=request.user, is_active=True).update(is_active=False)
        
        # Kreiranje nove lokacije
        DriverLocation.objects.create(
            driver=request.user,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            speed=speed,
            heading=heading
        )
        
        return JsonResponse({'success': True, 'message': 'Lokacija ažurirana.'})
    
    return JsonResponse({'success': False, 'message': 'Neispravna metoda.'})


@login_required
def premium_subscription_view(request):
    """Upravljanje premium pretplatom - B2B funkcionalnost"""
    try:
        subscription = request.user.premium_subscription
    except PremiumSubscription.DoesNotExist:
        subscription = None
    
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        
        # Definisanje cena i popusta
        subscription_data = {
            'basic': {'fee': 2000.00, 'discount': 5.00, 'limit': 0.00},
            'premium': {'fee': 5000.00, 'discount': 10.00, 'limit': 50000.00},
            'enterprise': {'fee': 15000.00, 'discount': 15.00, 'limit': 200000.00},
        }
        
        data = subscription_data.get(subscription_type)
        if data:
            if subscription:
                subscription.subscription_type = subscription_type
                subscription.monthly_fee = data['fee']
                subscription.discount_percentage = data['discount']
                subscription.deferred_payment_limit = data['limit']
                subscription.end_date = timezone.now() + timezone.timedelta(days=30)
                subscription.is_active = True
                subscription.save()
            else:
                PremiumSubscription.objects.create(
                    user=request.user,
                    subscription_type=subscription_type,
                    monthly_fee=data['fee'],
                    discount_percentage=data['discount'],
                    deferred_payment_limit=data['limit'],
                    end_date=timezone.now() + timezone.timedelta(days=30)
                )
            
            messages.success(request, f'Premium pretplata ({subscription_type}) je aktivirana!')
            return redirect('transport:premium_subscription')
    
    context = {
        'subscription': subscription,
        'subscription_types': PremiumSubscription.SUBSCRIPTION_TYPES
    }
    return render(request, 'transport/premium_subscription.html', context)


@login_required
def create_tour(request):
    """Kreiranje nove ture za prevoznika"""
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'prevoznik':
        messages.error(request, 'Nemate dozvolu za kreiranje tura.')
        return redirect('home')
    
    vehicle_license = request.GET.get('vehicle')
    vehicle = None
    
    if vehicle_license:
        try:
            vehicle = Vehicle.objects.get(
                license_plate=vehicle_license, 
                owner=request.user, 
                is_available=True
            )
        except Vehicle.DoesNotExist:
            messages.error(request, 'Vozilo nije pronađeno ili nije dostupno.')
            return redirect('transport:carrier_dashboard')
    
    if request.method == 'POST':
        form = TourForm(
            request.POST, 
            user=request.user, 
            vehicle_license=vehicle_license
        )
        
        if form.is_valid():
            try:
                # Create Tour object in database
                tour = Tour.objects.create(
                    driver=request.user,
                    vehicle=vehicle,
                    polaziste=form.cleaned_data['polaziste'],
                    odrediste=form.cleaned_data['odrediste'],
                    planirana_putanja=form.cleaned_data.get('planirana_putanja', ''),
                    dostupno_za_dotovar=form.cleaned_data.get('dostupno_za_dotovar', False),
                    kapacitet=form.cleaned_data.get('kapacitet', 0),
                    slobodna_kilaza=form.cleaned_data.get('slobodna_kilaza', 0),
                    status='active',
                    start_time=timezone.now()
                )
                
                # Mark vehicle as unavailable during tour
                if vehicle:
                    vehicle.is_available = False
                    vehicle.save()
                
                # Create initial location record
                Location.objects.create(
                    tour=tour,
                    latitude=0.0,  # Will be updated by GPS
                    longitude=0.0,  # Will be updated by GPS
                    timestamp=timezone.now()
                )
                
                # Create notification for tour start
                Notification.objects.create(
                    user=request.user,
                    title='Tura pokrenuta',
                    message=f'Tura {tour.polaziste} → {tour.odrediste} je uspešno pokrenuta. GPS praćenje je aktivno.',
                    notification_type='tour_started',
                    is_read=False
                )
                
                messages.success(
                    request, 
                    f'Tura uspešno kreirana! Polazište: {tour.polaziste}, Odredište: {tour.odrediste}. GPS praćenje je aktivno.'
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Tura uspešno kreirana! GPS praćenje je aktivno.',
                        'tour_id': tour.id,
                        'redirect_url': '/transport/carrier-dashboard/'
                    })
                
                return redirect('transport:carrier_dashboard')
                
            except Exception as e:
                messages.error(request, f'Greška pri kreiranju ture: {str(e)}')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Greška pri kreiranju ture: {str(e)}'
                    })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                })
    else:
        form = TourForm(user=request.user, vehicle_license=vehicle_license)
    
    context = {
        'form': form,
        'vehicle': vehicle,
        'vehicle_license': vehicle_license,
    }
    
    return render(request, 'transport/create_tour.html', context)


@login_required
def update_tour_location(request):
    """Update tour location via GPS - AJAX endpoint"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        data = json.loads(request.body)
        tour_id = data.get('tour_id')
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Get active tour for this user
        tour = Tour.objects.get(
            id=tour_id,
            driver=request.user,
            status__in=['confirmed', 'in_progress']
        )
        
        # Create location record
        location = Location.objects.create(
            tour=tour,
            latitude=latitude,
            longitude=longitude,
            timestamp=timezone.now()
        )
        
        # Update tour status to in progress if it was confirmed
        if tour.status == 'confirmed':
            tour.status = 'in_progress'
            tour.save()
        
        return JsonResponse({
            'success': True,
            'tour_completed': False,
            'location_id': location.id
        })
        
    except Tour.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tura nije pronađena'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def check_destination_proximity(tour, current_lat, current_lng):
    """Check if current location is within 5km of destination"""
    # This is a simplified distance calculation
    # In production, you'd use proper geospatial calculations
    
    # For now, return False - implement proper GPS coordinate parsing and distance calculation
    # when destination coordinates are available
    
    # TODO: Parse destination coordinates and calculate distance
    # destination_coords = parse_destination_coordinates(tour.odrediste)
    # if destination_coords:
    #     distance = calculate_distance(current_lat, current_lng, dest_lat, dest_lng)
    #     return distance <= 5.0  # 5km radius
    
    return False

# Stripe integration and cargo system views
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Add utility functions that are referenced but not defined
def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates using Haversine formula"""
    try:
        # Convert degrees to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [float(lat1), float(lng1), float(lat2), float(lng2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of Earth in kilometers
        return c * r
    except (ValueError, TypeError):
        return 0

def calculate_price(pallet_count, distance_km):
    """Calculate price based on pallet count and distance"""
    # Get price table
    try:
        price_table = CenaPoKilometrazi.objects.get(broj_paleta=pallet_count)
        if distance_km <= 200:
            base_price = price_table.cena_do_200km
        else:
            base_price = price_table.cena_preko_200km
    except CenaPoKilometrazi.DoesNotExist:
        # Fallback pricing
        base_price = 1000 * pallet_count
    
    total_price = base_price * max(1, (distance_km / 100))  # Adjust based on distance
    return {'base_price': base_price, 'total_price': total_price}

def get_eco_suggestion(weight):
    """Get eco-friendly packaging suggestion"""
    try:
        weight = float(weight)
        if weight < 100:
            return "Preporučujemo papirnu ambalažu"
        elif weight < 500:
            return "Preporučujemo kartonsku ambalažu"
        else:
            return "Preporučujemo drvenu paletu sa recikliranim materijalom"
    except (ValueError, TypeError):
        return "Preporučujemo odgovarajuću ambalažu za vaš teret"

def calculate_carrier_price(total_price):
    """Calculate carrier price (85% of total)"""
    try:
        return float(total_price) * 0.85
    except (ValueError, TypeError):
        return 0

@login_required
def cargo_map_view(request):
    """Display cargo map interface with Stripe integration"""
    context = {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'transport/cargo_map.html', context)

@login_required
@require_http_methods(['POST'])
def calculate_price_view(request):
    """Calculate price for cargo based on distance and pallet count"""
    try:
        data = json.loads(request.body)
        pickup_lat = data.get('pickup_lat')
        pickup_lng = data.get('pickup_lng')
        delivery_lat = data.get('delivery_lat')
        delivery_lng = data.get('delivery_lng')
        pallet_count = data.get('pallet_count', 1)
        weight = data.get('weight', 0)
        
        # Calculate distance using geopy
        distance_km = calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        
        # Calculate price using utility function
        price_data = calculate_price(pallet_count, distance_km)
        
        # Get eco suggestion
        eco_suggestion = get_eco_suggestion(weight)
        
        return JsonResponse({
            'success': True,
            'distance_km': distance_km,
            'pallet_count': pallet_count,
            'weight': weight,
            'base_price': price_data['base_price'],
            'total_price': price_data['total_price'],
            'eco_suggestion': eco_suggestion
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(['POST'])
def create_cargo_view(request):
    """Create cargo shipment with Stripe PaymentIntent"""
    try:
        data = json.loads(request.body)
        
        # Calculate price
        pickup_lat = data.get('pickup_lat')
        pickup_lng = data.get('pickup_lng')
        delivery_lat = data.get('delivery_lat')
        delivery_lng = data.get('delivery_lng')
        pallet_count = data.get('pallet_count', 1)
        weight = data.get('weight', 0)
        
        distance_km = calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        price_data = calculate_price(pallet_count, distance_km)
        
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(price_data['total_price'] * 100),  # Convert to cents
            currency='rsd',
            metadata={
                'user_id': request.user.id,
                'pallet_count': pallet_count,
                'distance_km': distance_km
            },
            capture_method='manual'  # Manual capture after delivery confirmation
        )
        
        # Create Cargo object
        cargo = Cargo.objects.create(
            shipper=request.user,
            pickup_address=data.get('pickup_address'),
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            delivery_address=data.get('delivery_address'),
            delivery_lat=delivery_lat,
            delivery_lng=delivery_lng,
            pallet_count=pallet_count,
            weight=weight,
            description=data.get('description', ''),
            price=price_data['total_price'],
            distance_km=distance_km,
            payment_intent_id=intent.id,
            status='pending_payment'
        )
        
        # Create notification for carriers
        Notification.objects.create(
            user=request.user,
            title="Nova Pošiljka Kreirana",
            message=f"Kreirana pošiljka od {pallet_count} paleta za {price_data['total_price']} RSD",
            notification_type='cargo'
        )
        
        return JsonResponse({
            'success': True,
            'client_secret': intent.client_secret,
            'cargo_id': cargo.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def cargo_list_view(request):
    """List cargo shipments for current user"""
    if request.user.profile.role == 'naručilac':
        cargos = Cargo.objects.filter(shipper=request.user).order_by('-created_at')
    else:
        cargos = Cargo.objects.filter(status__in=['pending_carrier', 'accepted']).order_by('-created_at')
    
    return render(request, 'transport/cargo_list.html', {'cargos': cargos})

@login_required
def cargo_detail_view(request, cargo_id):
    """Display cargo details"""
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    # Check permissions
    if cargo.shipper != request.user and cargo.carrier != request.user:
        return HttpResponseForbidden()
    
    return render(request, 'transport/cargo_detail.html', {'cargo': cargo})

@login_required
@require_http_methods(['POST'])
def accept_cargo_view(request, cargo_id):
    """Carrier accepts cargo shipment"""
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    if cargo.status != 'pending_carrier':
        return JsonResponse({'success': False, 'error': 'Pošiljka nije dostupna'})
    
    # Calculate carrier price (85% of total price)
    carrier_price = calculate_carrier_price(cargo.price)
    
    cargo.carrier = request.user
    cargo.status = 'accepted'
    cargo.carrier_price = carrier_price
    cargo.save()
    
    # Create notifications
    Notification.objects.create(
        user=cargo.shipper,
        title="Pošiljka Prihvaćena",
        message=f"Prevoznik {request.user.get_full_name()} je prihvatio vašu pošiljku",
        notification_type='cargo'
    )
    
    Notification.objects.create(
        user=request.user,
        title="Pošiljka Prihvaćena",
        message=f"Prihvatili ste pošiljku. Zarada: {carrier_price} RSD",
        notification_type='payment'
    )
    
    return JsonResponse({'success': True})

@login_required
@require_http_methods(['POST'])
def confirm_delivery_view(request, cargo_id):
    """Confirm delivery and capture Stripe payment"""
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    if cargo.shipper != request.user:
        return JsonResponse({'success': False, 'error': 'Nemate dozvolu'})
    
    if cargo.status != 'in_transit':
        return JsonResponse({'success': False, 'error': 'Pošiljka nije u tranzitu'})
    
    try:
        # Capture Stripe payment
        stripe.PaymentIntent.capture(cargo.payment_intent_id)
        
        cargo.status = 'delivered'
        cargo.delivered_at = timezone.now()
        cargo.save()
        
        # Create notifications
        Notification.objects.create(
            user=cargo.carrier,
            title="Dostava Potvrđena",
            message=f"Dostava je potvrđena. Zarada: {cargo.carrier_price} RSD",
            notification_type='payment'
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def notifications_api(request):
    """API endpoint for fetching notifications"""
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:10]
    
    data = {
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'notification_type': n.notification_type,
            'sound_file': n.sound_file,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        } for n in notifications]
    }
    
    return JsonResponse(data)

@login_required
@require_http_methods(['POST'])
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required
@require_http_methods(['POST'])
def notification_action(request, notification_id):
    """Handle notification action"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    data = json.loads(request.body)
    action = data.get('action')
    
    # Handle different actions based on notification type
    redirect_url = None
    
    if action == 'view_cargo':
        redirect_url = f'/transport/cargo-list/'
    elif action == 'accept_cargo':
        redirect_url = f'/transport/cargo-list/'
    elif action == 'view_dashboard':
        if request.user.profile.role == 'naručilac':
            redirect_url = '/transport/shipper-dashboard/'
        else:
            redirect_url = '/transport/carrier-dashboard/'
    
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True, 'redirect': redirect_url})

@csrf_exempt
@require_http_methods(['POST'])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Update cargo status
        try:
            cargo = Cargo.objects.get(payment_intent_id=payment_intent['id'])
            if cargo.status == 'pending_payment':
                cargo.status = 'pending_carrier'
                cargo.save()
        except Cargo.DoesNotExist:
            pass
    
    return HttpResponse(status=200)

@login_required
@require_http_methods(['POST'])
def stripe_cancel_subscription(request):
    """Cancel Stripe subscription (placeholder for future premium features)"""
    return JsonResponse({'success': True, 'message': 'Subscription cancelled'})

@login_required
@require_http_methods(['POST'])
def start_transport_view(request, cargo_id):
    """Start transport for cargo shipment"""
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    if cargo.carrier != request.user:
        return JsonResponse({'success': False, 'error': 'Nemate dozvolu'})
    
    if cargo.status != 'accepted':
        return JsonResponse({'success': False, 'error': 'Pošiljka nije u odgovarajućem statusu'})
    
    cargo.status = 'in_transit'
    cargo.started_at = timezone.now()
    cargo.save()
    
    # Create notifications
    Notification.objects.create(
        user=cargo.shipper,
        title="Transport Počet",
        message=f"Prevoznik je počeo transport vaše pošiljke #{cargo.id}",
        notification_type='cargo',
        sound_file='ping'
    )
    
    return JsonResponse({'success': True})

# PWA Views
def pwa_manifest(request):
    """PWA Manifest JSON"""
    manifest = {
        "name": "Tovar Taxi - Transport Platform",
        "short_name": "Tovar Taxi",
        "description": "Platforma za efikasno upravljanje transportom",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#2ECC71",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "/static/images/TTaxi.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/TTaxi.png",
                "sizes": "512x512", 
                "type": "image/png",
                "purpose": "maskable any"
            }
        ],
        "categories": ["business", "logistics", "transport"],
        "lang": "sr"
    }
    return JsonResponse(manifest)


def service_worker(request):
    """Service Worker for PWA"""
    sw_content = """
const CACHE_NAME = 'tovar-taxi-v1';
const urlsToCache = [
    '/',
    '/static/css/responsive.css',
    '/static/js/notifications.js',
    '/static/images/TTaxi.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});
"""
    return HttpResponse(sw_content, content_type='application/javascript')

def pwa_manifest(request):
    """PWA Manifest for adding app to home screen"""
    manifest = {
        "name": "Tovar Taxi",
        "short_name": "TovarTaxi",
        "description": "Aplikacija za prevoz tereta",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#667eea",
        "orientation": "portrait",
        "icons": [
            {
                "src": "/static/images/TTaxi.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "maskable any"
            },
            {
                "src": "/static/images/TTaxi.png", 
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable any"
            }
        ],
        "categories": ["business", "productivity", "transportation"],
        "lang": "sr"
    }
    return JsonResponse(manifest)

@login_required
def vehicle_details(request, vehicle_id):
    """Detalji vozila"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    context = {
        'vehicle': vehicle,
    }
    return render(request, 'transport/vehicle_details.html', context)


@login_required
def edit_vehicle(request, vehicle_id):
    """Izmena vozila"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'POST':
        # Extract form data
        license_plate = request.POST.get('license_plate')
        vehicle_brand = request.POST.get('vehicle_brand')
        vehicle_color = request.POST.get('vehicle_color')
        transport_license = request.POST.get('transport_license')
        vehicle_type = request.POST.get('vehicle_type')
        loading_height = request.POST.get('loading_height')
        payload_capacity = request.POST.get('payload_capacity')
        
        # Validation
        errors = []
        if not license_plate:
            errors.append('Registarski broj je obavezan')
        if not vehicle_brand:
            errors.append('Marka vozila je obavezna')
        if not vehicle_color:
            errors.append('Boja vozila je obavezna')
        if not transport_license:
            errors.append('Broj dozvole za prevoz tereta je obavezan')
        if not vehicle_type:
            errors.append('Tip vozila je obavezan')
        if not loading_height:
            errors.append('Visina utovarnog dela je obavezna')
        if not payload_capacity:
            errors.append('Tovarna nosivost je obavezna')
            
        # Check if license plate already exists (excluding current vehicle)
        if Vehicle.objects.filter(license_plate=license_plate).exclude(id=vehicle_id).exists():
            errors.append('Vozilo sa ovim registarskim brojem već postoji')
        
        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors})
            for error in errors:
                messages.error(request, error)
            return render(request, 'transport/edit_vehicle.html', {'vehicle': vehicle})
        
        try:
            # Convert capacity from kg to tons
            capacity_tons = float(payload_capacity) / 1000
            
            # Update vehicle
            vehicle.license_plate = license_plate
            vehicle.vehicle_brand = vehicle_brand
            vehicle.vehicle_color = vehicle_color
            vehicle.transport_license = transport_license
            vehicle.vehicle_type = vehicle_type
            vehicle.loading_height = int(loading_height)
            vehicle.capacity = capacity_tons
            vehicle.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Vozilo je uspešno ažurirano!'
                })
            
            messages.success(request, 'Vozilo je uspešno ažurirano!')
            return redirect('transport:manage_vehicles')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': f'Greška pri ažuriranju vozila: {str(e)}'})
            messages.error(request, f'Greška pri ažuriranju vozila: {str(e)}')
    
    context = {
        'vehicle': vehicle,
    }
    return render(request, 'transport/edit_vehicle.html', context)

def signup_sender_new_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        company_name = request.POST.get('company_name')
        tip_robe = request.POST.get('tip_robe')
        kolicina = request.POST.get('kolicina')
        opis_posiljke = request.POST.get('opis_posiljke')
        remember_me = request.POST.get('remember_me')
        
        # Validation
        if not all([username, email, password1, password2, phone_number, address]):
            messages.error(request, 'Molimo popunite sva obavezna polja.')
            return render(request, 'transport/signup_sender_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'tip_robe': tip_robe,
                'kolicina': kolicina,
                'opis_posiljke': opis_posiljke,
            })
        
        if password1 != password2:
            messages.error(request, 'Lozinke se ne poklapaju.')
            return render(request, 'transport/signup_sender_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'tip_robe': tip_robe,
                'kolicina': kolicina,
                'opis_posiljke': opis_posiljke,
            })
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Korisničko ime već postoji.')
            return render(request, 'transport/signup_sender_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'tip_robe': tip_robe,
                'kolicina': kolicina,
                'opis_posiljke': opis_posiljke,
            })
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email adresa već postoji.')
            return render(request, 'transport/signup_sender_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'tip_robe': tip_robe,
                'kolicina': kolicina,
                'opis_posiljke': opis_posiljke,
            })
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Create profile
            profile = Profile.objects.create(
                user=user,
                role='naručilac',
                phone_number=phone_number,
                address=address,
                company_name=company_name
            )
            
            # Login user
            login(request, user)
            
            # Set session expiry based on remember_me
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser session
            
            messages.success(request, 'Uspešno ste se registrovali!')
            return redirect('transport:shipper_dashboard')
            
        except Exception as e:
            messages.error(request, f'Greška pri registraciji: {str(e)}')
            return render(request, 'transport/signup_sender_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'tip_robe': tip_robe,
                'kolicina': kolicina,
                'opis_posiljke': opis_posiljke,
            })
    
    return render(request, 'transport/signup_sender_new.html')


def signup_carrier_new_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        company_name = request.POST.get('company_name')
        pib = request.POST.get('pib')
        tip_vozila = request.POST.get('tip_vozila')
        registarski_broj = request.POST.get('registarski_broj')
        remember_me = request.POST.get('remember_me')
        
        # Validation
        if not all([username, email, password1, password2, phone_number, address, company_name, pib, tip_vozila, registarski_broj]):
            messages.error(request, 'Molimo popunite sva obavezna polja.')
            return render(request, 'transport/signup_carrier_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            })
        
        if password1 != password2:
            messages.error(request, 'Lozinke se ne poklapaju.')
            return render(request, 'transport/signup_carrier_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            })
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Korisničko ime već postoji.')
            return render(request, 'transport/signup_carrier_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            })
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email adresa već postoji.')
            return render(request, 'transport/signup_carrier_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            })
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            
            # Create profile
            profile = Profile.objects.create(
                user=user,
                role='prevoznik',
                phone_number=phone_number,
                address=address,
                company_name=company_name
            )
            
            # Login user
            login(request, user)
            
            # Set session expiry based on remember_me
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Browser session
            
            messages.success(request, 'Uspešno ste se registrovali!')
            return redirect('transport:carrier_dashboard')
            
        except Exception as e:
            messages.error(request, f'Greška pri registraciji: {str(e)}')
            return render(request, 'transport/signup_carrier_new.html', {
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            })
    
    return render(request, 'transport/signup_carrier_new.html')
