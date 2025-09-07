from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
import stripe
import json
from .models import Cargo, Notification, Profile, CenaPoKilometrazi, Vehicle
from .utils import izracunaj_cenu, izracunaj_udaljenost, predlozi_eko_ambalazu, izracunaj_cenu_za_prevoznika
from django.conf import settings

# Stripe konfiguracija
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

@login_required
def cargo_mapa(request):
    """Stranica sa mapom za kreiranje nove rezervacije tereta"""
    if request.method == 'POST':
        try:
            # Uzmi podatke iz forme
            tezina = float(request.POST.get('tezina'))
            broj_paleta = int(request.POST.get('broj_paleta'))
            polazna_lat = float(request.POST.get('polazna_lat'))
            polazna_lon = float(request.POST.get('polazna_lon'))
            polazna_adresa = request.POST.get('polazna_adresa')
            odredisna_lat = float(request.POST.get('odredisna_lat'))
            odredisna_lon = float(request.POST.get('odredisna_lon'))
            odredisna_adresa = request.POST.get('odredisna_adresa')
            opis_tereta = request.POST.get('opis_tereta', '')
            
            # Izračunaj udaljenost
            udaljenost = izracunaj_udaljenost(polazna_lat, polazna_lon, odredisna_lat, odredisna_lon)
            
            # Izračunaj cenu za pošiljaoce
            cena_za_posiljaoce = izracunaj_cenu(broj_paleta, udaljenost)
            
            # Izračunaj cenu za prevoznika (minus 15%)
            cena_za_prevoznika, app_fee = izracunaj_cenu_za_prevoznika(cena_za_posiljaoce)
            
            # Predlog eko-ambalaže
            eko_ambalaza = predlozi_eko_ambalazu(tezina)
            
            # Kreiraj Stripe PaymentIntent (rezervacija)
            if stripe.api_key:
                intent = stripe.PaymentIntent.create(
                    amount=int(cena_za_posiljaoce * 100),  # u centima
                    currency='rsd',
                    capture_method='manual',  # rezervacija bez naplate
                    metadata={
                        'posiljilac_id': request.user.id,
                        'broj_paleta': broj_paleta,
                        'udaljenost': udaljenost
                    }
                )
                payment_intent_id = intent.id
                client_secret = intent.client_secret
            else:
                payment_intent_id = f"test_{timezone.now().timestamp()}"
                client_secret = "test_client_secret"
            
            # Sačuvaj cargo objekat
            cargo = Cargo.objects.create(
                posiljilac=request.user,
                tezina=tezina,
                broj_paleta=broj_paleta,
                opis_tereta=opis_tereta,
                polazna_latitude=polazna_lat,
                polazna_longitude=polazna_lon,
                polazna_adresa=polazna_adresa,
                odredisna_latitude=odredisna_lat,
                odredisna_longitude=odredisna_lon,
                odredisna_adresa=odredisna_adresa,
                udaljenost_km=udaljenost,
                cena_za_posiljaoce=cena_za_posiljaoce,
                cena_za_prevoznika=cena_za_prevoznika,
                app_fee=app_fee,
                payment_intent_id=payment_intent_id,
                eko_ambalaza=eko_ambalaza,
                status='reserved'
            )
            
            # Kreiraj notifikaciju za pošiljaoce
            Notification.objects.create(
                user=request.user,
                message=f"Nova rezervacija kreirana - {broj_paleta} paleta, {udaljenost:.1f}km, {cena_za_posiljaoce} RSD",
                sound_file='ping.mp3'
            )
            
            return JsonResponse({
                'success': True,
                'cargo_id': cargo.id,
                'client_secret': client_secret,
                'cena_za_posiljaoce': cena_za_posiljaoce,
                'cena_za_prevoznika': cena_za_prevoznika,
                'app_fee': app_fee,
                'udaljenost': udaljenost,
                'eko_ambalaza': eko_ambalaza
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - prikaži formu
    cene = CenaPoKilometrazi.objects.all().order_by('broj_paleta')
    return render(request, 'transport/cargo_mapa.html', {
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'cene': cene
    })

@login_required
def potvrdi_istovar(request, cargo_id):
    """Potvrda istovara i isplata prevozniku"""
    cargo = get_object_or_404(Cargo, id=cargo_id)
    
    # Proveri da li je korisnik prevoznik za ovaj teret
    if request.user.profile.role != 'prevoznik' or cargo.prevoznik != request.user:
        messages.error(request, 'Nemate dozvolu za ovu akciju.')
        return redirect('transport:carrier_dashboard')
    
    if request.method == 'POST' and cargo.status == 'in_transit':
        try:
            # Izvrši Stripe capture (isplata) ako postoji
            if stripe.api_key and cargo.payment_intent_id and not cargo.payment_intent_id.startswith('test_'):
                stripe.PaymentIntent.capture(cargo.payment_intent_id)
            
            # Ažuriraj status
            cargo.status = 'paid'
            cargo.isporucen = timezone.now()
            cargo.save()
            
            # Notifikacija za pošiljaoce
            Notification.objects.create(
                user=cargo.posiljilac,
                message=f"Teret isporučen i plaćanje potvrđeno - {cargo.cena_za_posiljaoce} RSD",
                sound_file='success.wav'
            )
            
            # Notifikacija za prevoznika sa cenom minus 15%
            Notification.objects.create(
                user=request.user,
                message=f"Isplata potvrđena - {cargo.cena_za_prevoznika} RSD (ukupno: {cargo.cena_za_posiljaoce} RSD, app fee: {cargo.app_fee} RSD)",
                sound_file='success.wav'
            )
            
            messages.success(request, f'Istovar potvrđen! Vaša zarada: {cargo.cena_za_prevoznika} RSD')
            
        except Exception as e:
            messages.error(request, f'Greška pri potvrdi: {str(e)}')
    
    return render(request, 'transport/potvrdi_istovar.html', {'cargo': cargo})

@login_required
def lista_tereta(request):
    """Lista tereta za pošiljaoce i prevoznike"""
    if request.user.profile.role == 'naručilac':
        tereti = Cargo.objects.filter(posiljilac=request.user).order_by('-kreiran')
        template = 'transport/lista_tereta_posiljilac.html'
    elif request.user.profile.role == 'prevoznik':
        # Prikaži dostupne tereti i dodeljene tereti
        dostupni_tereti = Cargo.objects.filter(status='reserved', prevoznik__isnull=True).order_by('-kreiran')
        moji_tereti = Cargo.objects.filter(prevoznik=request.user).order_by('-kreiran')
        return render(request, 'transport/lista_tereta_prevoznik.html', {
            'dostupni_tereti': dostupni_tereti,
            'moji_tereti': moji_tereti
        })
    else:
        tereti = Cargo.objects.none()
        template = 'transport/lista_tereta_posiljilac.html'
    
    return render(request, template, {'tereti': tereti})

@login_required
def prihvati_teret(request, cargo_id):
    """Prevoznik prihvata teret"""
    if request.user.profile.role != 'prevoznik':
        return JsonResponse({'success': False, 'error': 'Nemate dozvolu'})
    
    cargo = get_object_or_404(Cargo, id=cargo_id, status='reserved', prevoznik__isnull=True)
    
    # Dodeli teret prevozniku
    cargo.prevoznik = request.user
    cargo.status = 'assigned'
    cargo.save()
    
    # Notifikacija za pošiljaoce
    Notification.objects.create(
        user=cargo.posiljilac,
        message=f"Vaš teret je prihvaćen od strane prevoznika {request.user.get_full_name() or request.user.username}",
        sound_file='ping.mp3'
    )
    
    # Notifikacija za prevoznika sa cenom minus 15%
    Notification.objects.create(
        user=request.user,
        message=f"Prihvatili ste teret - Vaša zarada: {cargo.cena_za_prevoznika} RSD (od ukupno {cargo.cena_za_posiljaoce} RSD)",
        sound_file='success.wav'
    )
    
    return JsonResponse({'success': True, 'message': 'Teret uspešno prihvaćen!'})

def notifikacije_api(request):
    """API za dobijanje notifikacija"""
    if request.user.is_authenticated:
        notifikacije = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).order_by('-created_at')[:5]
        
        data = [{
            'id': n.id,
            'message': n.message,
            'sound_file': n.sound_file,
            'created_at': n.created_at.isoformat()
        } for n in notifikacije]
        
        # Označi kao pročitane
        notifikacije.update(is_read=True)
        
        return JsonResponse({'notifikacije': data})
    
    return JsonResponse({'notifikacije': []})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import (
    Profile, Vehicle, Shipment, ShipmentOffer, Tour, ChatMessage, Notification, Location,
    InstantDelivery, FoodDelivery, PaymentReservation, DriverLocation, PremiumSubscription, Cargo, CenaPoKilometrazi
)
from .forms import SignupForm, ShipmentForm, VehicleForm, ShipmentOfferForm, TourForm


def test_view(request):
    """Test view da proverim da li se Django view-ovi pozivaju"""
    print("TEST VIEW CALLED!")
    messages.success(request, "TEST VIEW RADI!")
    return JsonResponse({'status': 'success', 'message': 'Test view radi!'})


def home_view(request):
    """Glavna stranica aplikacije"""
    try:
        # Statistike za sve korisnike
        context = {
            'total_shipments': Shipment.objects.filter(status='published').count(),
            'total_carriers': Profile.objects.filter(role='prevoznik').count(),
            'total_vehicles': Vehicle.objects.filter(is_available=True).count(),
        }
        print(f"[DEBUG] Home view context: {context}")
        return render(request, 'transport/home.html', context)
    except Exception as e:
        print(f"[ERROR] Home view error: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        # Fallback context
        context = {
            'total_shipments': 0,
            'total_carriers': 0,
            'total_vehicles': 0,
        }
        return render(request, 'transport/home.html', context)


def signup_view(request):
    """Registracija korisnika"""
    print(f"[DEBUG] signup_view called - Method: {request.method}")
    
    if request.method == 'POST':
        print(f"[DEBUG] POST data received: {request.POST}")
        form = SignupForm(request.POST)
        print(f"[DEBUG] Form created, is_valid: {form.is_valid()}")
        
        if form.is_valid():
            print("[DEBUG] Form is valid, creating user...")
            user = form.save()
            print(f"[DEBUG] User created: {user.username}")
            
            profile = Profile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                phone_number=form.cleaned_data['phone_number'],
                address=form.cleaned_data['address'],
                company_name=form.cleaned_data.get('company_name', '')
            )
            print(f"[DEBUG] Profile created: {profile.id}")
            
            login(request, user)
            print(f"[DEBUG] User logged in: {user.is_authenticated}")
            
            messages.success(request, f'Dobrodošli {user.first_name}! Uspešno ste se registrovali.')
            
            # Role-based redirect
            if form.cleaned_data['role'] == 'naručilac':
                print("[DEBUG] Redirecting to create_shipment_request")
                return redirect('transport:create_shipment_request')
            elif form.cleaned_data['role'] in ['prevoznik', 'vozač']:
                print("[DEBUG] Redirecting to create_route_availability")
                return redirect('transport:create_route_availability')
            else:
                print("[DEBUG] Redirecting to home")
                return redirect('home')
        else:
            print(f"[DEBUG] Form errors: {form.errors}")
            messages.error(request, 'Greška u registraciji. Proverite unete podatke.')
    else:
        print("[DEBUG] GET request, creating empty form")
        form = SignupForm()
    
    print("[DEBUG] Rendering signup template")
    return render(request, 'transport/signup.html', {'form': form})


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

# Stripe integration and cargo system views
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

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
            notification_type='cargo',
            sound_file='success'
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
        notification_type='cargo',
        sound_file='success'
    )
    
    Notification.objects.create(
        user=request.user,
        title="Pošiljka Prihvaćena",
        message=f"Prihvatili ste pošiljku. Zarada: {carrier_price} RSD",
        notification_type='payment',
        sound_file='success'
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
            notification_type='payment',
            sound_file='success'
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
