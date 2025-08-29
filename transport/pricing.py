from decimal import Decimal
from django.conf import settings

class PricingCalculator:
    """
    Dinamički kalkulator cena za transport na osnovu:
    - Osnovne cene po kilometru
    - Hitnosti pošiljke 
    - Broja paleta
    - Tipa rute (autoput/magistrala)
    """
    
    # Osnovne cene po kilometru (RSD)
    BASE_PRICE_PER_KM = {
        'van': Decimal('25.0'),      # Kombi
        'truck': Decimal('35.0'),    # Kamion  
        'trailer': Decimal('45.0'),  # Šleper
        'mega': Decimal('45.0'),     # Mega trailer
    }
    
    # Multiplikatori za hitnost
    URGENCY_MULTIPLIERS = {
        'standard': Decimal('1.0'),   # Standardno
        'today': Decimal('2.5'),      # Danas za danas - hitno
        'asap': Decimal('1.8'),       # Što pre moguće
        'weekend': Decimal('1.4'),    # Uključiti subotu
    }
    
    # Cena po paleti
    PALLET_BASE_PRICE = Decimal('500.0')  # RSD po paleti
    
    # Multiplikatori za tip puta
    ROUTE_MULTIPLIERS = {
        'highway': Decimal('1.0'),     # Autoput - najjeftiniji
        'main_road': Decimal('1.1'),   # Magistralni put
        'regional': Decimal('1.2'),    # Regionalni put
        'local': Decimal('1.3'),       # Lokalni put
    }
    
    @classmethod
    def calculate_price(cls, distance_km, vehicle_type, urgency='standard', 
                       pallet_count=1, route_type='highway'):
        """
        Izračunava ukupnu cenu transporta
        
        Args:
            distance_km: Rastojanje u kilometrima
            vehicle_type: Tip vozila (van, truck, trailer, mega)
            urgency: Hitnost (standard, today, asap, weekend)
            pallet_count: Broj paleta
            route_type: Tip rute (highway, main_road, regional, local)
            
        Returns:
            Decimal: Ukupna cena u RSD
        """
        if not distance_km or distance_km <= 0:
            return Decimal('0.0')
            
        # Osnovna cena po kilometru
        base_km_price = cls.BASE_PRICE_PER_KM.get(vehicle_type, cls.BASE_PRICE_PER_KM['truck'])
        
        # Cena na osnovu rastojanja
        distance_price = base_km_price * Decimal(str(distance_km))
        
        # Cena paleta
        pallet_price = cls.PALLET_BASE_PRICE * pallet_count
        
        # Osnovna cena
        base_total = distance_price + pallet_price
        
        # Primeni multiplikator hitnosti
        urgency_multiplier = cls.URGENCY_MULTIPLIERS.get(urgency, Decimal('1.0'))
        
        # Primeni multiplikator rute
        route_multiplier = cls.ROUTE_MULTIPLIERS.get(route_type, Decimal('1.0'))
        
        # Finalna cena
        final_price = base_total * urgency_multiplier * route_multiplier
        
        # Zaokruži na najbliže 50 dinara
        final_price = (final_price / 50).quantize(Decimal('1')) * 50
        
        return final_price
    
    @classmethod
    def get_price_breakdown(cls, distance_km, vehicle_type, urgency='standard',
                           pallet_count=1, route_type='highway'):
        """
        Vraća detaljnu strukturu cene
        """
        base_km_price = cls.BASE_PRICE_PER_KM.get(vehicle_type, cls.BASE_PRICE_PER_KM['truck'])
        distance_price = base_km_price * Decimal(str(distance_km))
        pallet_price = cls.PALLET_BASE_PRICE * pallet_count
        base_total = distance_price + pallet_price
        
        urgency_multiplier = cls.URGENCY_MULTIPLIERS.get(urgency, Decimal('1.0'))
        route_multiplier = cls.ROUTE_MULTIPLIERS.get(route_type, Decimal('1.0'))
        
        final_price = base_total * urgency_multiplier * route_multiplier
        final_price = (final_price / 50).quantize(Decimal('1')) * 50
        
        return {
            'distance_km': distance_km,
            'base_price_per_km': base_km_price,
            'distance_price': distance_price,
            'pallet_count': pallet_count,
            'pallet_price': pallet_price,
            'base_total': base_total,
            'urgency': urgency,
            'urgency_multiplier': urgency_multiplier,
            'route_type': route_type,
            'route_multiplier': route_multiplier,
            'final_price': final_price
        }


class WaitingTimePenalty:
    """
    Sistem penala za kašnjenje
    15 minuta = 500 RSD
    """
    
    PENALTY_PER_15MIN = Decimal('500.0')
    
    @classmethod
    def calculate_penalty(cls, minutes_late):
        """
        Izračunava penal za kašnjenje
        
        Args:
            minutes_late: Broj minuta kašnjenja
            
        Returns:
            Decimal: Penal u RSD
        """
        if minutes_late <= 0:
            return Decimal('0.0')
            
        # Svaki započeti period od 15 minuta se naplaćuje
        periods = (minutes_late + 14) // 15  # Ceiling division
        
        return cls.PENALTY_PER_15MIN * periods
    
    @classmethod
    def get_penalty_breakdown(cls, minutes_late):
        """
        Vraća detaljnu strukturu penala
        """
        if minutes_late <= 0:
            return {
                'minutes_late': 0,
                'periods': 0,
                'penalty_per_period': cls.PENALTY_PER_15MIN,
                'total_penalty': Decimal('0.0')
            }
            
        periods = (minutes_late + 14) // 15
        total_penalty = cls.PENALTY_PER_15MIN * periods
        
        return {
            'minutes_late': minutes_late,
            'periods': periods,
            'penalty_per_period': cls.PENALTY_PER_15MIN,
            'total_penalty': total_penalty
        }
