from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import json
from .models import (
    Profile, Shipment, Vehicle, ShipmentOffer, City, Route,
    Tour, Transaction, ChatMessage, TourNotification
)
from .forms import SignUpForm, ShipmentForm, VehicleForm, ShipmentOfferForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

def terms_and_conditions(request):
    return render(request, 'transport/terms_and_conditions.html')

def signup_view(request):
    return render(request, 'transport/signup.html')

def signup_sender_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                user_type='shipper',
                phone_number=form.cleaned_data.get('phone_number'),
                address=form.cleaned_data.get('address')
            )
            login(request, user)
            messages.success(request, 'Uspešno ste se registrovali kao Naručilac transporta!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Molimo ispravite greške u formi.')
    else:
        form = SignUpForm()
    return render(request, 'transport/signup_sender.html', {'form': form})

def signup_carrier_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile with carrier type
            Profile.objects.create(
                user=user,
                user_type='carrier',
                phone_number=form.cleaned_data.get('phone_number', ''),
                address=form.cleaned_data.get('address', ''),
                company_name=form.cleaned_data.get('company_name', ''),
                tax_number=form.cleaned_data.get('tax_number', '')
            )
            login(request, user)
            messages.success(request, 'Uspešno ste se registrovali kao Prevoznik!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Molimo ispravite greške u formi.')
    else:
        form = SignUpForm()
    return render(request, 'transport/signup_carrier.html', {'form': form})

def home_view(request):
    return render(request, 'transport/home.html')

@login_required
def freight_exchange(request):
    shipments = Shipment.objects.select_related('shipper', 'carrier').order_by('-created_at')
    cities = City.objects.filter(is_major=True).order_by('name')
    
    # Base filtering
    user_type = getattr(request.user.profile, 'user_type', None) if hasattr(request.user, 'profile') else None
    
    if user_type == 'carrier':
        # Carriers see published shipments (not their own)
        shipments = shipments.filter(status='published').exclude(shipper=request.user)
    elif user_type == 'shipper':
        # Shippers see their own shipments
        shipments = shipments.filter(shipper=request.user)
    else:
        shipments = shipments.filter(status='published')
    
    # Apply filters
    pickup_city_id = request.GET.get('pickup_city')
    delivery_city_id = request.GET.get('delivery_city')
    cargo_type = request.GET.get('cargo_type')
    max_weight = request.GET.get('max_weight')
    min_price = request.GET.get('min_price')
    pickup_date = request.GET.get('pickup_date')
    status = request.GET.get('status')
    my_offers = request.GET.get('my_offers')
    
    if pickup_city_id:
        try:
            city = City.objects.get(id=pickup_city_id)
            shipments = shipments.filter(Q(pickup_city=city.name) | Q(pickup_region=city.region))
        except City.DoesNotExist:
            pass
    
    if delivery_city_id:
        try:
            city = City.objects.get(id=delivery_city_id)
            shipments = shipments.filter(Q(delivery_city=city.name) | Q(delivery_region=city.region))
        except City.DoesNotExist:
            pass
    
    if cargo_type:
        shipments = shipments.filter(cargo_type=cargo_type)
    
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
    
    if status:
        shipments = shipments.filter(status=status)
    
    if my_offers and user_type == 'carrier':
        shipments = shipments.filter(offers__carrier=request.user).distinct()
    
    # Pagination
    paginator = Paginator(shipments, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'shipments': page_obj,
        'cities': cities,
        'user_type': user_type,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'last_updated': timezone.now(),
    }
    
    return render(request, 'transport/freight_exchange.html', context)

@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user)
        profile = request.user.profile
    
    context = {
        'profile': profile,
        'user_type': profile.user_type,
    }
    
    if profile.user_type == 'shipper':
        context.update({
            'total_shipments': request.user.shipments.count(),
            'active_shipments': request.user.shipments.filter(status__in=['published', 'assigned', 'in_transit']).count(),
            'recent_shipments': request.user.shipments.all()[:5],
        })
    elif profile.user_type == 'carrier':
        context.update({
            'total_vehicles': request.user.vehicles.count(),
            'active_vehicles': request.user.vehicles.filter(is_active=True).count(),
            'total_offers': ShipmentOffer.objects.filter(carrier=request.user).count(),
            'accepted_offers': ShipmentOffer.objects.filter(carrier=request.user, is_accepted=True).count(),
            'recent_offers': ShipmentOffer.objects.filter(carrier=request.user).order_by('-created_at')[:5],
        })
    
    return render(request, 'transport/dashboard.html', context)

@login_required
def create_shipment(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.shipper = request.user
            
            # Handle city selection
            if form.cleaned_data.get('pickup_city'):
                city = form.cleaned_data['pickup_city']
                shipment.pickup_city = city.name
                shipment.pickup_postal_code = city.postal_code
                if not shipment.pickup_region:
                    shipment.pickup_region = city.region
                    
            if form.cleaned_data.get('delivery_city'):
                city = form.cleaned_data['delivery_city']
                shipment.delivery_city = city.name
                shipment.delivery_postal_code = city.postal_code
                if not shipment.delivery_region:
                    shipment.delivery_region = city.region
            
            # Set status based on action
            action = request.POST.get('action', 'draft')
            shipment.status = 'published' if action == 'publish' else 'draft'
            
            shipment.save()
            
            # Generate route suggestions if both cities are selected
            if shipment.pickup_city and shipment.delivery_city:
                generate_route_suggestions(shipment)
            
            success_msg = 'Pošiljka je uspešno objavljena!' if action == 'publish' else 'Pošiljka je sačuvana kao nacrt!'
            messages.success(request, success_msg)
            return redirect('shipment_detail', pk=shipment.pk)
    else:
        form = ShipmentForm()
    
    return render(request, 'transport/create_shipment.html', {'form': form})

@login_required
def freight_exchange_view(request):
    shipments = Shipment.objects.filter(status='published').select_related('shipper__profile')
    
    # Filters
    city_filter = request.GET.get('city')
    cargo_type_filter = request.GET.get('cargo_type')
    
    if city_filter:
        shipments = shipments.filter(
            Q(pickup_city__icontains=city_filter) | Q(delivery_city__icontains=city_filter)
        )
    
    if cargo_type_filter:
        shipments = shipments.filter(cargo_type=cargo_type_filter)
    
    context = {
        'shipments': shipments,
        'city_filter': city_filter,
        'cargo_type_filter': cargo_type_filter,
        'cargo_types': [('general', 'Opšti teret'), ('fragile', 'Krhki teret'), ('hazardous', 'Opasni teret')],
    }
    return render(request, 'transport/freight_exchange.html', context)

@login_required
def shipment_detail_view(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    offers = shipment.offers.all().select_related('carrier__profile', 'vehicle')
    
    context = {
        'shipment': shipment,
        'offers': offers,
        'can_make_offer': (
            hasattr(request.user, 'profile') and 
            request.user.profile.user_type == 'carrier' and
            not offers.filter(carrier=request.user).exists()
        ),
    }
    return render(request, 'transport/shipment_detail.html', context)

@login_required
def make_offer_view(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check if user is carrier and hasn't made an offer yet
    if not (hasattr(request.user, 'profile') and request.user.profile.user_type == 'carrier'):
        messages.error(request, 'Samo prevoznici mogu da prave ponude.')
        return redirect('shipment_detail', pk=pk)
    
    if ShipmentOffer.objects.filter(shipment=shipment, carrier=request.user).exists():
        messages.error(request, 'Već ste poslali ponudu za ovu pošiljku.')
        return redirect('shipment_detail', pk=pk)
    
    if request.method == 'POST':
        form = ShipmentOfferForm(request.POST, user=request.user)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.shipment = shipment
            offer.carrier = request.user
            offer.save()
            messages.success(request, 'Ponuda je uspešno poslata!')
            return redirect('shipment_detail', pk=pk)
    else:
        form = ShipmentOfferForm(user=request.user)
    
    context = {
        'form': form,
        'shipment': shipment,
    }
    return render(request, 'transport/make_offer.html', context)

@login_required
def manage_vehicles(request):
    vehicles = Vehicle.objects.filter(owner=request.user).order_by('-created_at')
    
    # Calculate stats
    total_vehicles = vehicles.count()
    active_vehicles = vehicles.filter(is_active=True).count()
    total_capacity = vehicles.aggregate(total=Sum('max_weight'))['total'] or 0
    assigned_vehicles = vehicles.filter(shipment_offers__is_accepted=True).distinct().count()
    
    context = {
        'vehicles': vehicles,
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'total_capacity': total_capacity,
        'assigned_vehicles': assigned_vehicles,
    }
    
    return render(request, 'transport/manage_vehicles.html', context)

@login_required
def settings_view(request):
    if request.method == 'POST':
        # Update user profile
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update profile
        profile = user.profile
        profile.phone_number = request.POST.get('phone_number', '')
        profile.address = request.POST.get('address', '')
        profile.company_name = request.POST.get('company_name', '')
        profile.tax_number = request.POST.get('tax_number', '')
        profile.save()
        
        messages.success(request, 'Podešavanja su uspešno sačuvana!')
        return redirect('settings')
    
    return render(request, 'transport/settings.html')


# ==================== TURE I CHAT VIEWS ====================

@login_required
def ture_list(request):
    """Prikaz svih tura korisnika"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user)
        profile = request.user.profile
    
    if profile.user_type == 'carrier':
        ture = Tour.objects.filter(vozac=request.user).order_by('-created_at')
    else:
        ture = Tour.objects.filter(narucilac=request.user).order_by('-created_at')
    
    context = {
        'ture': ture,
        'user_type': profile.user_type
    }
    return render(request, 'transport/ture_list.html', context)


@login_required
def tura_detail(request, tura_id):
    """Detaljan prikaz ture"""
    tura = get_object_or_404(Tour, id=tura_id)
    
    # Proveri dozvole
    if request.user not in [tura.vozac, tura.narucilac]:
        messages.error(request, 'Nemate dozvolu za pristup ovoj turi.')
        return redirect('ture_list')
    
    transakcije = tura.transakcije.all()
    
    context = {
        'tura': tura,
        'transakcije': transakcije,
        'is_vozac': request.user == tura.vozac,
        'is_narucilac': request.user == tura.narucilac
    }
    return render(request, 'transport/tura_detail.html', context)


@login_required
def chat_view(request, tura_id):
    """Chat između vozača i naručioca"""
    tura = get_object_or_404(Tour, id=tura_id)
    
    # Proveri dozvole
    if request.user not in [tura.vozac, tura.narucilac]:
        messages.error(request, 'Nemate dozvolu za pristup ovom chatu.')
        return redirect('ture_list')
    
    # Označi poruke kao pročitane
    tura.chat_poruke.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    poruke = tura.chat_poruke.all().select_related('sender')
    
    context = {
        'tura': tura,
        'poruke': poruke,
        'other_user': tura.narucilac if request.user == tura.vozac else tura.vozac
    }
    return render(request, 'transport/chat.html', context)


@login_required
def notifikacije_view(request):
    """Prikaz notifikacija korisnika"""
    notifikacije = request.user.tour_notifications.all().order_by('-created_at')[:50]
    
    # Označi kao pročitane kada korisnik otvori stranicu
    request.user.tour_notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifikacije': notifikacije
    }
    return render(request, 'transport/notifikacije.html', context)

def generate_route_suggestions(shipment):
    """Generate 3-5 route suggestions for a shipment"""
    try:
        pickup_city = City.objects.filter(name=shipment.pickup_city).first()
        delivery_city = City.objects.filter(name=shipment.delivery_city).first()
        
        if not pickup_city or not delivery_city:
            return
        
        # Find highways connecting these cities
        highways = Highway.objects.filter(
            Q(start_city=pickup_city, end_city=delivery_city) |
            Q(start_city=delivery_city, end_city=pickup_city) |
            Q(start_city__region=pickup_city.region, end_city__region=delivery_city.region)
        ).order_by('priority', 'highway_type')
        
        route_suggestions = [
            {'name': 'Najkraća ruta', 'highways': highways.filter(highway_type='highway')[:2], 'priority': 1, 'is_recommended': True},
            {'name': 'Najbrža ruta', 'highways': highways.filter(priority=1)[:3], 'priority': 2, 'is_recommended': False},
            {'name': 'Ekonomična ruta', 'highways': highways.filter(toll_road=False)[:2], 'priority': 3, 'is_recommended': False},
            {'name': 'Magistralna ruta', 'highways': highways.filter(highway_type='main_road')[:2], 'priority': 4, 'is_recommended': False},
            {'name': 'Regionalna ruta', 'highways': highways.filter(highway_type='regional')[:3], 'priority': 5, 'is_recommended': False},
        ]
        
        for i, suggestion in enumerate(route_suggestions):
            if suggestion['highways'].exists():
                route = Route.objects.create(
                    shipment=shipment,
                    name=suggestion['name'],
                    priority=suggestion['priority'],
                    is_recommended=suggestion['is_recommended']
                )
                
                # Add highways to route
                for order, highway in enumerate(suggestion['highways'], 1):
                    route.highways.add(highway, through_defaults={'order': order})
                    
    except Exception as e:
        print(f"Error generating routes: {e}")

# AJAX endpoints for vehicle management
@login_required
def vehicle_detail_api(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    data = {
        'vehicle_type': vehicle.vehicle_type,
        'license_plate': vehicle.license_plate,
        'max_weight': str(vehicle.max_weight),
        'max_volume': str(vehicle.max_volume),
        'length': str(vehicle.length) if vehicle.length else '',
        'width': str(vehicle.width) if vehicle.width else '',
        'height': str(vehicle.height) if vehicle.height else '',
        'is_active': vehicle.is_active,
    }
    return JsonResponse(data)

@login_required
def vehicle_add_api(request):
    if request.method == 'POST':
        try:
            vehicle = Vehicle.objects.create(
                owner=request.user,
                vehicle_type=request.POST.get('vehicle_type'),
                license_plate=request.POST.get('license_plate'),
                max_weight=float(request.POST.get('max_weight', 0)),
                max_volume=float(request.POST.get('max_volume', 0)),
                length=float(request.POST.get('length')) if request.POST.get('length') else None,
                width=float(request.POST.get('width')) if request.POST.get('width') else None,
                height=float(request.POST.get('height')) if request.POST.get('height') else None,
                is_active=request.POST.get('is_active') == 'on'
            )
            return JsonResponse({'success': True, 'vehicle_id': vehicle.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def vehicle_edit_api(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'POST':
        try:
            vehicle.vehicle_type = request.POST.get('vehicle_type')
            vehicle.license_plate = request.POST.get('license_plate')
            vehicle.max_weight = float(request.POST.get('max_weight', 0))
            vehicle.max_volume = float(request.POST.get('max_volume', 0))
            vehicle.length = float(request.POST.get('length')) if request.POST.get('length') else None
            vehicle.width = float(request.POST.get('width')) if request.POST.get('width') else None
            vehicle.height = float(request.POST.get('height')) if request.POST.get('height') else None
            vehicle.is_active = request.POST.get('is_active') == 'on'
            vehicle.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def vehicle_toggle_api(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            vehicle.is_active = data.get('is_active', False)
            vehicle.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def vehicle_delete_api(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'DELETE':
        try:
            vehicle.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
