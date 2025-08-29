"""
TOVAR TAXI - API VIEWS ZA TURE I NOTIFIKACIJE
Kompletni API endpoint-i za sve operacije
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
import json
import logging

from .models import (
    Tour, Transaction, ChatMessage, TourNotification, 
    Shipment, Vehicle, Profile
)

logger = logging.getLogger(__name__)

# ==================== TOUR API ====================

@csrf_exempt
@require_POST
@login_required
def kreiraj_turu(request):
    """API za kreiranje nove ture"""
    try:
        data = json.loads(request.body)
        
        # Validacija podataka
        required_fields = ['shipment_id', 'vehicle_id', 'vozac_id', 'cena']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Nedostaje polje: {field}'}, status=400)
        
        shipment = get_object_or_404(Shipment, id=data['shipment_id'])
        vehicle = get_object_or_404(Vehicle, id=data['vehicle_id'])
        vozac = get_object_or_404(User, id=data['vozac_id'])
        
        # Kreiranje ture
        with transaction.atomic():
            tura = Tour.objects.create(
                vozac=vozac,
                narucilac=shipment.shipper,
                shipment=shipment,
                vehicle=vehicle,
                pocetna_adresa=shipment.pickup_city,
                odredisna_adresa=shipment.delivery_city,
                datum_polaska=data.get('datum_polaska', timezone.now()),
                kolicina_tereta=shipment.weight,
                cena=data['cena'],
                tip_tereta=data.get('tip_tereta', ''),
                napomene=data.get('napomene', ''),
                kontakt_narucioca=shipment.shipper.profile.phone_number
            )
            
            # Kreiranje notifikacije za vozača
            TourNotification.objects.create(
                recipient=vozac,
                tura=tura,
                notification_type='nova_tura',
                title='🚛 Nova tura kreirana!',
                message=f'Kreirana je nova tura: {tura.pocetna_adresa} → {tura.odredisna_adresa}',
                action_type='potvrdi_turu',
                action_url=f'/api/ture/{tura.id}/potvrdi'
            )
            
            # Kreiranje transakcije
            Transaction.objects.create(
                tura=tura,
                iznos=tura.cena,
                status='rezervisano'
            )
        
        return JsonResponse({
            'success': True,
            'tura_id': tura.id,
            'message': 'Tura je uspešno kreirana'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Nevalidan JSON'}, status=400)
    except Exception as e:
        logger.error(f"Greška pri kreiranju ture: {str(e)}")
        return JsonResponse({'error': 'Greška pri kreiranju ture'}, status=500)


@csrf_exempt
@require_POST
@login_required
def potvrdi_turu(request, tura_id):
    """API za potvrđivanje ture od strane vozača"""
    try:
        tura = get_object_or_404(Tour, id=tura_id)
        
        # Proveri da li je korisnik vozač ove ture
        if request.user != tura.vozac:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        if tura.status != 'kreirana':
            return JsonResponse({'error': 'Tura je već obrađena'}, status=400)
        
        with transaction.atomic():
            # Ažuriraj status ture
            tura.status = 'potvrdjena'
            tura.save()
            
            # Rezerviši sredstva
            transakcija = tura.transakcije.first()
            if transakcija:
                transakcija.status = 'naplaceno'
                transakcija.save()
            
            # Notifikacija za naručioca
            TourNotification.objects.create(
                recipient=tura.narucilac,
                tura=tura,
                notification_type='tura_potvrdjena',
                title='✅ Tura potvrđena!',
                message=f'Vozač {tura.vozac.get_full_name()} je potvrdio vašu turu.',
                action_type='otvori_chat',
                action_url=f'/chat/{tura.id}/'
            )
            
            # Sistemska poruka u chat
            ChatMessage.objects.create(
                tura=tura,
                sender=tura.vozac,
                message_type='system',
                text_content=f'Vozač {tura.vozac.get_full_name()} je potvrdio turu. Kontaktirajte ga za dodatne detalje.'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Tura je uspešno potvrđena'
        })
        
    except Exception as e:
        logger.error(f"Greška pri potvrđivanju ture: {str(e)}")
        return JsonResponse({'error': 'Greška pri potvrđivanju ture'}, status=500)


@csrf_exempt
@require_POST
@login_required
def odbij_turu(request, tura_id):
    """API za odbijanje ture od strane vozača"""
    try:
        tura = get_object_or_404(Tour, id=tura_id)
        
        if request.user != tura.vozac:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        if tura.status != 'kreirana':
            return JsonResponse({'error': 'Tura je već obrađena'}, status=400)
        
        data = json.loads(request.body) if request.body else {}
        razlog = data.get('razlog', 'Vozač je odbio turu')
        
        with transaction.atomic():
            tura.status = 'otkazana'
            tura.napomene = f"Odbijeno: {razlog}"
            tura.save()
            
            # Otkaži transakciju
            transakcija = tura.transakcije.first()
            if transakcija:
                transakcija.status = 'otkazano'
                transakcija.save()
            
            # Notifikacija za naručioca
            TourNotification.objects.create(
                recipient=tura.narucilac,
                tura=tura,
                notification_type='tura_odbijena',
                title='❌ Tura odbijena',
                message=f'Vozač je odbio turu. Razlog: {razlog}',
                action_type='detalji_ture',
                action_url=f'/ture/{tura.id}/'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Tura je odbijena'
        })
        
    except Exception as e:
        logger.error(f"Greška pri odbijanju ture: {str(e)}")
        return JsonResponse({'error': 'Greška pri odbijanju ture'}, status=500)


@csrf_exempt
@require_POST
@login_required
def potvrdi_preuzimanje(request, tura_id):
    """API za potvrđivanje preuzimanja tereta"""
    try:
        tura = get_object_or_404(Tour, id=tura_id)
        
        if request.user != tura.vozac:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        if tura.status != 'potvrdjena':
            return JsonResponse({'error': 'Tura mora biti potvrđena pre preuzimanja'}, status=400)
        
        with transaction.atomic():
            tura.status = 'preuzeto'
            tura.preuzimanje_potvrdjeno = True
            tura.preuzimanje_vreme = timezone.now()
            tura.save()
            
            # Notifikacija za naručioca
            TourNotification.objects.create(
                recipient=tura.narucilac,
                tura=tura,
                notification_type='preuzimanje_potvrdjeno',
                title='📦 Teret preuzet!',
                message=f'Vozač je potvrdio preuzimanje tereta.',
                action_type='otvori_chat',
                action_url=f'/chat/{tura.id}/'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Preuzimanje je potvrđeno'
        })
        
    except Exception as e:
        logger.error(f"Greška pri potvrđivanju preuzimanja: {str(e)}")
        return JsonResponse({'error': 'Greška pri potvrđivanju preuzimanja'}, status=500)


@csrf_exempt
@require_POST
@login_required
def potvrdi_isporuku(request, tura_id):
    """API za potvrđivanje isporuke tereta"""
    try:
        tura = get_object_or_404(Tour, id=tura_id)
        
        if request.user != tura.vozac:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        if tura.status != 'preuzeto':
            return JsonResponse({'error': 'Teret mora biti preuzet pre isporuke'}, status=400)
        
        with transaction.atomic():
            tura.status = 'isporuceno'
            tura.isporuka_potvrdjena = True
            tura.isporuka_vreme = timezone.now()
            tura.save()
            
            # Isplati vozaču
            transakcija = tura.transakcije.first()
            if transakcija and transakcija.status == 'naplaceno':
                transakcija.status = 'isplaceno'
                transakcija.datum_isplate = timezone.now()
                transakcija.save()
            
            # Notifikacija za naručioca
            TourNotification.objects.create(
                recipient=tura.narucilac,
                tura=tura,
                notification_type='isporuka_potvrdjena',
                title='🎯 Teret isporučen!',
                message=f'Vozač je potvrdio isporuku tereta.',
                action_type='detalji_ture',
                action_url=f'/ture/{tura.id}/'
            )
            
            # Notifikacija za vozača o isplati
            TourNotification.objects.create(
                recipient=tura.vozac,
                tura=tura,
                notification_type='payment_processed',
                title='💰 Isplata obrađena!',
                message=f'Sredstva su prebačena na vaš račun: {transakcija.iznos - transakcija.provizija_iznos} RSD',
                action_type='detalji_ture',
                action_url=f'/ture/{tura.id}/'
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Isporuka je potvrđena i sredstva su isplaćena'
        })
        
    except Exception as e:
        logger.error(f"Greška pri potvrđivanju isporuke: {str(e)}")
        return JsonResponse({'error': 'Greška pri potvrđivanju isporuke'}, status=500)


# ==================== CHAT API ====================

@csrf_exempt
@require_POST
@login_required
def posalji_poruku(request, tura_id):
    """API za slanje chat poruke"""
    try:
        tura = get_object_or_404(Tour, id=tura_id)
        
        # Proveri da li korisnik učestvuje u ovoj turi
        if request.user not in [tura.vozac, tura.narucilac]:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        data = json.loads(request.body)
        message_type = data.get('message_type', 'text')
        
        poruka = ChatMessage.objects.create(
            tura=tura,
            sender=request.user,
            message_type=message_type,
            text_content=data.get('text_content', ''),
            location_lat=data.get('location_lat'),
            location_lng=data.get('location_lng')
        )
        
        # Notifikacija za drugu stranu
        recipient = tura.narucilac if request.user == tura.vozac else tura.vozac
        TourNotification.objects.create(
            recipient=recipient,
            tura=tura,
            notification_type='nova_poruka',
            title='💬 Nova poruka',
            message=f'{request.user.get_full_name()}: {poruka.text_content[:50]}...',
            action_type='otvori_chat',
            action_url=f'/chat/{tura.id}/'
        )
        
        return JsonResponse({
            'success': True,
            'poruka_id': poruka.id,
            'message': 'Poruka je poslana'
        })
        
    except Exception as e:
        logger.error(f"Greška pri slanju poruke: {str(e)}")
        return JsonResponse({'error': 'Greška pri slanju poruke'}, status=500)


@login_required
def get_chat_poruke(request, tura_id):
    """API za dobijanje chat poruka"""
    try:
        tura = get_object_or_404(Tour, id=tura_id)
        
        if request.user not in [tura.vozac, tura.narucilac]:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        poruke = tura.chat_poruke.all().select_related('sender')
        
        # Označi poruke kao pročitane
        tura.chat_poruke.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        
        poruke_data = []
        for poruka in poruke:
            poruke_data.append({
                'id': poruka.id,
                'sender': poruka.sender.get_full_name(),
                'sender_id': poruka.sender.id,
                'message_type': poruka.message_type,
                'text_content': poruka.text_content,
                'location_lat': str(poruka.location_lat) if poruka.location_lat else None,
                'location_lng': str(poruka.location_lng) if poruka.location_lng else None,
                'is_read': poruka.is_read,
                'created_at': poruka.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'poruke': poruke_data
        })
        
    except Exception as e:
        logger.error(f"Greška pri dobijanju poruka: {str(e)}")
        return JsonResponse({'error': 'Greška pri dobijanju poruka'}, status=500)


# ==================== NOTIFICATION API ====================

@login_required
def get_notifikacije(request):
    """API za dobijanje korisničkih notifikacija"""
    try:
        notifikacije = request.user.tour_notifications.filter(is_read=False)[:20]
        
        notifikacije_data = []
        for notif in notifikacije:
            notifikacije_data.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'notification_type': notif.notification_type,
                'action_type': notif.action_type,
                'action_url': notif.action_url,
                'tura_id': notif.tura.id,
                'created_at': notif.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'notifikacije': notifikacije_data,
            'count': len(notifikacije_data)
        })
        
    except Exception as e:
        logger.error(f"Greška pri dobijanju notifikacija: {str(e)}")
        return JsonResponse({'error': 'Greška pri dobijanju notifikacija'}, status=500)


@csrf_exempt
@require_POST
@login_required
def oznaci_notifikaciju_procitanu(request, notif_id):
    """API za označavanje notifikacije kao pročitane"""
    try:
        notifikacija = get_object_or_404(TourNotification, id=notif_id, recipient=request.user)
        notifikacija.is_read = True
        notifikacija.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notifikacija je označena kao pročitana'
        })
        
    except Exception as e:
        logger.error(f"Greška pri označavanju notifikacije: {str(e)}")
        return JsonResponse({'error': 'Greška pri označavanju notifikacije'}, status=500)


# ==================== PAYMENT API ====================

@csrf_exempt
@require_POST
@login_required
def rezervisi_sredstva(request):
    """API za rezervaciju sredstava za turu"""
    try:
        data = json.loads(request.body)
        tura_id = data.get('tura_id')
        payment_method = data.get('payment_method', 'card')
        
        tura = get_object_or_404(Tour, id=tura_id)
        
        if request.user != tura.narucilac:
            return JsonResponse({'error': 'Nemate dozvolu za ovu akciju'}, status=403)
        
        # Simulacija rezervacije sredstava
        transakcija = tura.transakcije.first()
        if transakcija:
            transakcija.payment_method = payment_method
            transakcija.payment_id = f"PAY_{tura_id}_{timezone.now().timestamp()}"
            transakcija.status = 'rezervisano'
            transakcija.save()
        
        return JsonResponse({
            'success': True,
            'transaction_id': transakcija.id,
            'message': 'Sredstva su rezervisana'
        })
        
    except Exception as e:
        logger.error(f"Greška pri rezervaciji sredstava: {str(e)}")
        return JsonResponse({'error': 'Greška pri rezervaciji sredstava'}, status=500)
