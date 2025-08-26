from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .forms import SignUpForm, ShipmentForm, VehicleForm, ShipmentOfferForm
from .models import Profile, Shipment, Vehicle, ShipmentOffer

def signup_view(request):
    return render(request, 'transport/signup.html')

def signup_sender_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile with shipper type
            Profile.objects.create(
                user=user,
                user_type='shipper',
                phone_number=form.cleaned_data.get('phone_number', ''),
                address=form.cleaned_data.get('address', ''),
                company_name=form.cleaned_data.get('company_name', ''),
                tax_number=form.cleaned_data.get('tax_number', '')
            )
            login(request, user)
            return redirect('dashboard')
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
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'transport/signup_carrier.html', {'form': form})

def home_view(request):
    return render(request, 'transport/home.html')

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
def create_shipment_view(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.shipper = request.user
            shipment.save()
            messages.success(request, 'Pošiljka je uspešno kreirana!')
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
def manage_vehicles_view(request):
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
    
    vehicles = request.user.vehicles.all()
    
    context = {
        'form': form,
        'vehicles': vehicles,
    }
    return render(request, 'transport/manage_vehicles.html', context)

def settings_view(request):
    return render(request, 'transport/settings.html')
