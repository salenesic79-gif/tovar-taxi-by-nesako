from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import re

class SecurityManager:
    """
    Sistem bezbednosti i odgovornosti za logističku platformu
    """
    
    # Pravila bezbednosti
    SECURITY_RULES = {
        'max_shipment_value': 1000000,  # Maksimalna vrednost pošiljke u RSD
        'max_weight_per_shipment': 25000,  # Maksimalna težina u kg
        'min_carrier_rating': 3.0,  # Minimalna ocena vozača
        'max_daily_shipments_per_carrier': 5,  # Maksimalno pošiljki po danu
        'verification_required_for_high_value': 500000,  # Verifikacija za vredne pošiljke
        'insurance_required_threshold': 100000,  # Obavezno osiguranje
    }
    
    @classmethod
    def validate_shipment_security(cls, shipment, carrier=None):
        """
        Validira bezbednost pošiljke pre dodele
        
        Returns:
            dict: {'valid': bool, 'warnings': list, 'errors': list}
        """
        warnings = []
        errors = []
        
        # Proveri vrednost pošiljke
        if shipment.offered_price > cls.SECURITY_RULES['max_shipment_value']:
            errors.append(f"Vrednost pošiljke ({shipment.offered_price} RSD) prelazi maksimalno dozvoljenu ({cls.SECURITY_RULES['max_shipment_value']} RSD)")
        
        # Proveri težinu
        if shipment.weight > cls.SECURITY_RULES['max_weight_per_shipment']:
            errors.append(f"Težina pošiljke ({shipment.weight} kg) prelazi maksimalno dozvoljenu ({cls.SECURITY_RULES['max_weight_per_shipment']} kg)")
        
        # Proveri verifikaciju za vredne pošiljke
        if shipment.offered_price > cls.SECURITY_RULES['verification_required_for_high_value']:
            if not shipment.shipper.profile.is_verified:
                errors.append("Naručilac mora biti verifikovan za pošiljke veće vrednosti")
        
        # Proveri osiguranje
        if shipment.offered_price > cls.SECURITY_RULES['insurance_required_threshold']:
            warnings.append("Preporučuje se osiguranje pošiljke zbog visoke vrednosti")
        
        # Proveri vozača ako je dodeljen
        if carrier:
            carrier_rating = cls.get_carrier_average_rating(carrier)
            if carrier_rating < cls.SECURITY_RULES['min_carrier_rating']:
                warnings.append(f"Vozač ima nisku ocenu ({carrier_rating:.1f}/5.0)")
            
            # Proveri dnevni limit
            daily_shipments = cls.get_carrier_daily_shipments(carrier)
            if daily_shipments >= cls.SECURITY_RULES['max_daily_shipments_per_carrier']:
                errors.append(f"Vozač je dostigao dnevni limit pošiljki ({daily_shipments})")
        
        # Proveri opasni teret
        if shipment.cargo_type == 'hazardous':
            warnings.append("Opasni teret zahteva posebne mere bezbednosti")
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors
        }
    
    @classmethod
    def validate_user_verification(cls, user):
        """
        Proverava status verifikacije korisnika
        """
        profile = getattr(user, 'profile', None)
        if not profile:
            return {'verified': False, 'missing': ['Profil nije kreiran']}
        
        missing_data = []
        
        if not profile.phone_number:
            missing_data.append('Broj telefona')
        
        if not profile.address:
            missing_data.append('Adresa')
        
        if profile.user_type == 'carrier':
            if not profile.company_name:
                missing_data.append('Naziv kompanije')
            if not profile.tax_number:
                missing_data.append('PIB')
            
            # Proveri vozila
            if not user.vehicles.filter(is_active=True).exists():
                missing_data.append('Aktivno vozilo')
        
        return {
            'verified': profile.is_verified and len(missing_data) == 0,
            'missing': missing_data
        }
    
    @classmethod
    def get_carrier_average_rating(cls, carrier):
        """
        Vraća prosečnu ocenu vozača
        """
        from .models import Rating
        
        ratings = Rating.objects.filter(
            rated_user=carrier,
            rating_type='shipper_to_carrier'
        )
        
        if not ratings.exists():
            return 5.0  # Novi vozači počinju sa 5.0
        
        total_stars = sum(rating.stars for rating in ratings)
        return total_stars / ratings.count()
    
    @classmethod
    def get_carrier_daily_shipments(cls, carrier):
        """
        Vraća broj pošiljki vozača za danas
        """
        from .models import Shipment
        
        today = timezone.now().date()
        return Shipment.objects.filter(
            carrier=carrier,
            created_at__date=today
        ).count()
    
    @classmethod
    def validate_phone_number(cls, phone):
        """
        Validira srpski broj telefona
        """
        # Srpski formati: +381..., 0..., 381...
        patterns = [
            r'^\+381[0-9]{8,9}$',  # +38163123456
            r'^0[0-9]{8,9}$',      # 063123456
            r'^381[0-9]{8,9}$',    # 381631234567
        ]
        
        for pattern in patterns:
            if re.match(pattern, phone):
                return True
        
        return False
    
    @classmethod
    def validate_tax_number(cls, tax_number):
        """
        Validira PIB (Poreski identifikacioni broj)
        """
        # PIB mora imati 9 cifara
        if not re.match(r'^\d{9}$', tax_number):
            return False
        
        # Kontrolna cifra algoritam
        digits = [int(d) for d in tax_number]
        
        # Izračunaj kontrolnu cifru
        sum_val = 0
        for i in range(8):
            sum_val += digits[i] * (8 - i)
        
        remainder = sum_val % 11
        
        if remainder < 2:
            control_digit = remainder
        else:
            control_digit = 11 - remainder
        
        return digits[8] == control_digit
    
    @classmethod
    def log_security_event(cls, event_type, user, description, shipment=None):
        """
        Beleži bezbednosni događaj
        """
        from .models import SecurityLog
        
        SecurityLog.objects.create(
            event_type=event_type,
            user=user,
            description=description,
            shipment=shipment,
            ip_address=cls.get_client_ip(),
            user_agent=cls.get_user_agent()
        )
    
    @classmethod
    def get_client_ip(cls):
        """Vraća IP adresu klijenta"""
        # TODO: Implementirati kada bude dostupan request objekat
        return "127.0.0.1"
    
    @classmethod
    def get_user_agent(cls):
        """Vraća User-Agent klijenta"""
        # TODO: Implementirati kada bude dostupan request objekat
        return "Unknown"


class ResponsibilityManager:
    """
    Upravljanje odgovornošću i pravilima korišćenja
    """
    
    RESPONSIBILITY_RULES = {
        'shipper_responsibilities': [
            "Tačno opisivanje tereta i njegove vrednosti",
            "Pravovremeno pripremanje pošiljke za preuzimanje", 
            "Obezbeđivanje pristupa za preuzimanje",
            "Plaćanje dogovorene cene u roku",
            "Poštovanje dogovorenih termina"
        ],
        
        'carrier_responsibilities': [
            "Bezbedna i pažljiva manipulacija teretom",
            "Poštovanje dogovorenih rokova dostave",
            "Redovno ažuriranje statusa pošiljke",
            "Profesionalno ponašanje prema klijentima",
            "Održavanje vozila u ispravnom stanju"
        ],
        
        'platform_responsibilities': [
            "Obezbeđivanje sigurne platforme za komunikaciju",
            "Zaštita ličnih podataka korisnika",
            "Podrška korisnicima tokom procesa",
            "Pravednost u rešavanju sporova",
            "Transparentnost u cenama i uslovima"
        ]
    }
    
    LIABILITY_LIMITS = {
        'platform_liability': 50000,  # RSD - maksimalna odgovornost platforme
        'carrier_liability_per_kg': 100,  # RSD po kilogramu
        'max_carrier_liability': 500000,  # RSD - maksimalna odgovornost vozača
    }
    
    @classmethod
    def get_user_agreement_text(cls, user_type):
        """
        Vraća tekst ugovora za tip korisnika
        """
        if user_type == 'shipper':
            return cls._get_shipper_agreement()
        elif user_type == 'carrier':
            return cls._get_carrier_agreement()
        else:
            return cls._get_general_agreement()
    
    @classmethod
    def _get_shipper_agreement(cls):
        """Ugovor za naručioce"""
        return """
# UGOVOR O KORIŠĆENJU - NARUČILAC TRANSPORTA

## VAŠE ODGOVORNOSTI:
- Tačno opisivanje tereta, težine i dimenzija
- Pravovremeno pripremanje pošiljke za preuzimanje
- Obezbeđivanje pristupa vozilu za utovar
- Plaćanje dogovorene cene u roku od 7 dana
- Poštovanje dogovorenih termina preuzimanja

## OGRANIČENJA ODGOVORNOSTI:
- Platforma ne odgovara za štetu veću od {platform_liability} RSD
- Vozač odgovara do {max_carrier_liability} RSD po pošiljci
- Obavezno je osiguranje za pošiljke veće od {insurance_threshold} RSD

## PENALI:
- Kašnjenje u pripremi tereta: 500 RSD po svakih 15 minuta
- Netačne informacije o teretu: do 10% vrednosti pošiljke
- Otkazivanje u poslednjem trenutku: 20% dogovorene cene

Korišćenjem platforme prihvatate ove uslove.
        """.format(
            platform_liability=cls.LIABILITY_LIMITS['platform_liability'],
            max_carrier_liability=cls.LIABILITY_LIMITS['max_carrier_liability'],
            insurance_threshold=SecurityManager.SECURITY_RULES['insurance_required_threshold']
        )
    
    @classmethod
    def _get_carrier_agreement(cls):
        """Ugovor za vozače"""
        return """
# UGOVOR O KORIŠĆENJU - PREVOZNIK

## VAŠE ODGOVORNOSTI:
- Bezbedna i pažljiva manipulacija teretom
- Poštovanje dogovorenih rokova dostave
- Redovno ažuriranje statusa pošiljke
- Profesionalno ponašanje prema klijentima
- Održavanje vozila u ispravnom stanju

## OGRANIČENJA ODGOVORNOSTI:
- Odgovarate za štetu do {carrier_liability_per_kg} RSD po kilogramu
- Maksimalna odgovornost: {max_carrier_liability} RSD po pošiljci
- Obavezno je osiguranje vozila i tereta

## PENALI:
- Kašnjenje u dostavi: 500 RSD po svakih 15 minuta
- Oštećenje tereta: puna vrednost štete
- Neprofesionalno ponašanje: suspenzija naloga

## ZARADA:
- Platforma zadržava 5% od svake transakcije
- Isplata se vrši u roku od 3 radna dana
- Bonusi za visoke ocene i pouzdanost

Korišćenjem platforme prihvatate ove uslove.
        """.format(
            carrier_liability_per_kg=cls.LIABILITY_LIMITS['carrier_liability_per_kg'],
            max_carrier_liability=cls.LIABILITY_LIMITS['max_carrier_liability']
        )
    
    @classmethod
    def _get_general_agreement(cls):
        """Opšti uslovi korišćenja"""
        return """
# OPŠTI USLOVI KORIŠĆENJA - TOVAR TAXI

## O PLATFORMI:
Tovar Taxi je B2B logistička platforma koja povezuje naručioce transporta sa prevoznicima.

## PRAVILA KORIŠĆENJA:
- Registracija je obavezna za sve korisnike
- Verifikacija je potrebna za transakcije veće vrednosti
- Zabranjeno je zloupotrebljavanje platforme
- Poštovanje svih korisnika je obavezno

## PRIVATNOST:
- Čuvamo vaše lične podatke u skladu sa zakonom
- Podaci se koriste samo za potrebe platforme
- Možete zatražiti brisanje svojih podataka

## PODRŠKA:
- Dostupni smo 24/7 za podršku
- Sporovi se rešavaju kroz medijaciju
- Konačna odluka je na platformi

Korišćenjem platforme prihvatate ove uslove.
        """
    
    @classmethod
    def calculate_liability(cls, shipment, damage_type='full'):
        """
        Izračunava odgovornost za štetu
        """
        if damage_type == 'full':
            # Puna šteta
            carrier_liability = min(
                float(shipment.offered_price),
                cls.LIABILITY_LIMITS['max_carrier_liability']
            )
        else:
            # Šteta po kilogramu
            carrier_liability = min(
                float(shipment.weight) * cls.LIABILITY_LIMITS['carrier_liability_per_kg'],
                cls.LIABILITY_LIMITS['max_carrier_liability']
            )
        
        platform_liability = min(
            carrier_liability * 0.1,  # 10% od vozačeve odgovornosti
            cls.LIABILITY_LIMITS['platform_liability']
        )
        
        return {
            'carrier_liability': carrier_liability,
            'platform_liability': platform_liability,
            'total_coverage': carrier_liability + platform_liability
        }
