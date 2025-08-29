from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import Profile, Vehicle, Shipment, ShipmentOffer, Tour, ChatMessage, Notification, Location
from .forms import SignupForm, ShipmentForm, VehicleForm, ShipmentOfferForm


def home_view(request):
    """Glavna stranica aplikacije"""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.role == 'naručilac':
                return redirect('shipper_dashboard')
            elif profile.role == 'prevoznik':
                return redirect('carrier_dashboard')
            elif profile.role == 'vozač':
                return redirect('driver_dashboard')
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
            return redirect('home')
    else:
        form = SignupForm()
    
    return render(request, 'registration/signup.html', {'form': form})


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
    if request.user.profile.role != 'prevoznik':
        return redirect('home')
    
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
        request.user.profile.role == 'prevoznik' or
        request.user.is_staff
    )
    
    if not can_view:
        messages.error(request, 'Nemate dozvolu da vidite ovu pošiljku.')
        return redirect('home')
    
    context = {
        'shipment': shipment,
        'offers': offers,
        'can_make_offer': request.user.profile.role == 'prevoznik' and shipment.status == 'published',
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
    if request.user.profile.role != 'prevoznik':
        return redirect('home')
    
    vehicles = Vehicle.objects.filter(owner=request.user).order_by('-created_at')
    
    context = {
        'vehicles': vehicles,
    }
    return render(request, 'transport/manage_vehicles.html', context)


@login_required
def add_vehicle(request):
    """Dodavanje novog vozila"""
    if request.user.profile.role != 'prevoznik':
        return redirect('home')
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, 'Vozilo je uspešno dodato!')
            return redirect('manage_vehicles')
    else:
        form = VehicleForm()
    
    return render(request, 'transport/add_vehicle.html', {'form': form})


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
