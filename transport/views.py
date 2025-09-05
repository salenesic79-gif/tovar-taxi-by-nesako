from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import (
    Profile, Vehicle, Shipment, ShipmentOffer, Tour, ChatMessage, Notification, Location,
    InstantDelivery, FoodDelivery, PaymentReservation, DriverLocation, PremiumSubscription
)
from .forms import SignupForm, ShipmentForm, VehicleForm, ShipmentOfferForm, TourForm


def test_view(request):
    """Test view da proverim da li se Django view-ovi pozivaju"""
    print("TEST VIEW CALLED!")
    messages.success(request, "TEST VIEW RADI!")
    return JsonResponse({'status': 'success', 'message': 'Test view radi!'})


def home_view(request):
    """Glavna stranica aplikacije"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.role == 'naručilac':
                return redirect('transport:create_shipment_request')
            elif profile.role in ['prevoznik', 'vozač']:
                return redirect('transport:create_route_availability')
        except Profile.DoesNotExist:
            pass
    
    # Statistike za neregistrovane korisnike
    context = {
        'total_shipments': Shipment.objects.filter(status='published').count(),
        'total_carriers': Profile.objects.filter(role='prevoznik').count(),
        'total_vehicles': Vehicle.objects.filter(is_available=True).count(),
    }
    return render(request, 'transport/home.html', context)


def signup_view(request):
    """Registracija korisnika"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                company_name=form.cleaned_data['company_name']
            )
            login(request, user)
            messages.success(request, 'Uspešno ste se registrovali!')
            if form.cleaned_data['role'] == 'naručilac':
                return redirect('transport:create_shipment_request')
            elif form.cleaned_data['role'] in ['prevoznik', 'vozač']:
                return redirect('transport:create_route_availability')
    else:
        form = SignupForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@csrf_exempt
def signup_sender_view(request):
    """Registracija naručioca"""
    if request.method == 'POST':
        # Extract form fields
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        company_name = request.POST.get('company_name', '')
        pib = request.POST.get('pib', '')
        maticni_broj = request.POST.get('maticni_broj', '')
        terms_accepted = request.POST.get('terms_accepted')
        
        # Validation
        errors = []
        
        if not terms_accepted:
            errors.append('Morate prihvatiti uslove korišćenja.')
        
        if password1 != password2:
            errors.append('Lozinke se ne poklapaju.')
        
        if len(password1) < 8:
            errors.append('Lozinka mora imati najmanje 8 karaktera.')
        
        if User.objects.filter(username=username).exists():
            errors.append('Korisničko ime je već u upotrebi. Molimo kreirajte drugo.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email adresa je već registrovana.')
        
        if not username or not email or not password1 or not first_name or not last_name:
            errors.append('Sva obavezna polja moraju biti popunjena.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'maticni_broj': maticni_broj,
            }
            return render(request, 'registration/signup_sender.html', context)
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            profile = Profile.objects.create(
                user=user,
                role='naručilac',
                phone_number=phone_number,
                address=address,
                company_name=company_name,
                pib=pib,
                maticni_broj=maticni_broj
            )
            
            login(request, user)
            messages.success(request, 'Uspešno ste se registrovali!')
            return redirect('transport:create_shipment_request')
            
        except Exception as e:
            messages.error(request, f'Greška pri registraciji: {str(e)}')
            context = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'maticni_broj': maticni_broj,
            }
            return render(request, 'registration/signup_sender.html', context)
    
    return render(request, 'registration/signup_sender.html')


def signup_carrier_view(request):
    """Registracija prevoznika"""
    if request.method == 'POST':
        # Extract form fields
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        company_name = request.POST.get('company_name')
        pib = request.POST.get('pib', '')
        maticni_broj = request.POST.get('maticni_broj', '')
        vozačka_dozvola = request.POST.get('vozačka_dozvola', '')
        tip_vozila = request.POST.get('tip_vozila', '')
        registarski_broj = request.POST.get('registarski_broj', '')
        terms_accepted = request.POST.get('terms_accepted')
        
        # Validation
        errors = []
        
        if not terms_accepted:
            errors.append('Morate prihvatiti uslove korišćenja.')
        
        if password1 != password2:
            errors.append('Lozinke se ne poklapaju.')
        
        if len(password1) < 8:
            errors.append('Lozinka mora imati najmanje 8 karaktera.')
        
        if User.objects.filter(username=username).exists():
            errors.append('Korisničko ime je već u upotrebi. Molimo kreirajte drugo.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email adresa je već registrovana.')
        
        if not username or not email or not password1 or not first_name or not last_name:
            errors.append('Sva obavezna polja moraju biti popunjena.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            context = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'maticni_broj': maticni_broj,
                'vozačka_dozvola': vozačka_dozvola,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            }
            return render(request, 'registration/signup_carrier.html', context)
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create profile
            profile = Profile.objects.create(
                user=user,
                role='prevoznik',
                phone_number=phone_number,
                address=address,
                company_name=company_name,
                pib=pib,
                maticni_broj=maticni_broj,
                vozačka_dozvola=vozačka_dozvola
            )
            
            # Create default vehicle
            Vehicle.objects.create(
                owner=user,
                vehicle_type=tip_vozila or 'kamion',
                license_plate=registarski_broj or f"TEMP-{user.id}",
                capacity=1000,
                is_available=True
            )
            
            login(request, user)
            messages.success(request, 'Uspešno ste se registrovali!')
            return redirect('transport:carrier_dashboard')
            
        except Exception as e:
            messages.error(request, f'Greška pri registraciji: {str(e)}')
            context = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'address': address,
                'company_name': company_name,
                'pib': pib,
                'maticni_broj': maticni_broj,
                'vozačka_dozvola': vozačka_dozvola,
                'tip_vozila': tip_vozila,
                'registarski_broj': registarski_broj,
            }
            return render(request, 'registration/signup_carrier.html', context)
    
    return render(request, 'registration/signup_carrier.html')


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
def driver_dashboard(request):
    """Dashboard za vozače"""
    if request.user.profile.role != 'vozač':
        return redirect('home')
    
    tours = Tour.objects.filter(driver=request.user).order_by('-created_at')
    active_tours = tours.filter(status__in=['confirmed', 'in_progress', 'pickup_confirmed'])
    
    context = {
        'tours': tours[:10],
        'active_tours': active_tours,
        'total_tours': tours.count(),
        'completed_tours': tours.filter(status='completed').count(),
    }
    return render(request, 'transport/driver_dashboard.html', context)


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
        request.user.profile.role in ['prevoznik', 'vozač'] or
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
    if request.user.profile.role not in ['prevoznik', 'vozač']:
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
    shipments = Shipment.objects.filter(status='published').order_by('-created_at')
    
    # Filtriranje
    pickup_city = request.GET.get('pickup_city')
    delivery_city = request.GET.get('delivery_city')
    cargo_type = request.GET.get('cargo_type')
    
    if pickup_city:
        shipments = shipments.filter(pickup_city__icontains=pickup_city)
    if delivery_city:
        shipments = shipments.filter(delivery_city__icontains=delivery_city)
    if cargo_type:
        shipments = shipments.filter(cargo_type__icontains=cargo_type)
    
    # Paginacija
    paginator = Paginator(shipments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pickup_city': pickup_city,
        'delivery_city': delivery_city,
        'cargo_type': cargo_type,
    }
    return render(request, 'transport/freight_exchange.html', context)


@login_required
def manage_vehicles(request):
    """Upravljanje vozilima"""
    if request.user.profile.role not in ['prevoznik', 'vozač']:
        return redirect('home')
    
    vehicles = Vehicle.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'vehicles': vehicles,
    }
    return render(request, 'transport/manage_vehicles.html', context)


@login_required
def add_vehicle(request):
    """Dodavanje novog vozila - AJAX compatible"""
    if request.user.profile.role not in ['prevoznik', 'vozač']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Nemate dozvolu za dodavanje vozila'})
        return redirect('home')
    
    if request.method == 'POST':
        # Extract form data
        license_plate = request.POST.get('license_plate')
        vehicle_brand = request.POST.get('vehicle_brand')
        vehicle_color = request.POST.get('vehicle_color')
        transport_license = request.POST.get('transport_license')
        insurance_policy = request.POST.get('insurance_policy', '')
        insurance_amount = request.POST.get('insurance_amount', '')
        vehicle_type = request.POST.get('vehicle_type')
        loading_height = request.POST.get('loading_height')
        payload_capacity = request.POST.get('payload_capacity')
        fleet_size = request.POST.get('fleet_size')
        specializations = request.POST.getlist('specializations')
        coverage_areas = request.POST.getlist('coverage_areas')
        
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
        if not fleet_size:
            errors.append('Broj vozila u floti je obavezan')
            
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
            # Create vehicle
            vehicle = Vehicle.objects.create(
                owner=request.user,
                license_plate=license_plate,
                vehicle_brand=vehicle_brand,
                vehicle_color=vehicle_color,
                transport_license=transport_license,
                insurance_policy=insurance_policy,
                insurance_amount=insurance_amount or None,
                vehicle_type=vehicle_type,
                loading_height=int(loading_height),
                capacity=int(payload_capacity),
                fleet_size=fleet_size,
                specializations=','.join(specializations) if specializations else '',
                coverage_areas=','.join(coverage_areas) if coverage_areas else '',
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
                    'brand_code': get_brand_code(vehicle.vehicle_brand)
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


def get_brand_code(brand):
    """Helper function to get brand code for license plate display"""
    brand_codes = {
        'mercedes': 'MB',
        'volvo': 'VO', 
        'scania': 'SC',
        'man': 'MN',
        'daf': 'DF',
        'iveco': 'IV',
        'renault': 'RN',
        'ford': 'FD',
        'isuzu': 'IS',
        'fiat': 'FT'
    }
    return brand_codes.get(brand, '??')


@login_required
def my_tours(request):
    """Lista tura korisnika"""
    if request.user.profile.role == 'vozač':
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
    
    messages = ChatMessage.objects.filter(tour=tour).order_by('timestamp')
    
    context = {
        'tour': tour,
        'messages': messages,
        'can_chat': tour.driver == request.user or tour.shipment.sender == request.user,
    }
    return render(request, 'transport/tour_detail.html', context)


@login_required
def notifications(request):
    """Lista notifikacija"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Označi sve kao pročitane
    notifications.filter(is_read=False).update(is_read=True)
    
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
        driver=offer.carrier
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
    print(f"DEBUG: custom_login_view called, method: {request.method}")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"DEBUG: Attempting login for username: {username}")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"DEBUG: Authentication successful for {username}")
            login(request, user)
            
            # Role-based redirect
            try:
                profile = user.profile
                print(f"DEBUG: User {username} has profile with role: {profile.role}")
                
                if profile.role == 'naručilac':
                    print("DEBUG: Redirecting to shipper_dashboard")
                    return redirect('transport:shipper_dashboard')
                elif profile.role in ['prevoznik', 'vozač']:
                    print("DEBUG: Redirecting to carrier_dashboard (prevoznik/vozač)")
                    return redirect('transport:carrier_dashboard')
                else:
                    print(f"DEBUG: Unknown role '{profile.role}', redirecting to home")
                    return redirect('home')
            except Profile.DoesNotExist:
                print(f"DEBUG: Profile does not exist for user {username}, redirecting to home")
                # Ako nema profil, idi na home
                return redirect('home')
        else:
            print(f"DEBUG: Authentication failed for username: {username}")
            messages.error(request, 'Neispravno korisničko ime ili lozinka.')
    
    print("DEBUG: Rendering login template")
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
    """Prošireni dashboard za vozače sa instant i food delivery"""
    if request.user.profile.role not in ['prevoznik', 'vozač']:
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
    return render(request, 'transport/driver_dashboard_extended.html', context)


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
            status='active'
        )
        
        # Create location record
        location = Location.objects.create(
            tour=tour,
            latitude=latitude,
            longitude=longitude,
            timestamp=timezone.now()
        )
        
        # Check if tour is near destination (5km radius)
        destination_reached = check_destination_proximity(tour, latitude, longitude)
        
        if destination_reached:
            # Complete the tour
            tour.status = 'completed'
            tour.end_time = timezone.now()
            tour.save()
            
            # Make vehicle available again
            if tour.vehicle:
                tour.vehicle.is_available = True
                tour.vehicle.save()
            
            # Create completion notification
            Notification.objects.create(
                user=request.user,
                title='Tura završena',
                message=f'Tura {tour.polaziste} → {tour.odrediste} je automatski završena jer ste stigli na odredište.',
                notification_type='tour_completed',
                is_read=False
            )
            
            return JsonResponse({
                'success': True,
                'tour_completed': True,
                'message': 'Tura je automatski završena - stigli ste na odredište!'
            })
        
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
