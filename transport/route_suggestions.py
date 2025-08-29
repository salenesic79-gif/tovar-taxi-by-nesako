from django.db.models import Q
from .models import City, Highway, Route, RouteHighway, Shipment
from decimal import Decimal
import math

class RouteSuggestionEngine:
    """
    Sistem za automatsko predlaganje ruta između gradova
    """
    
    @classmethod
    def suggest_routes(cls, pickup_city_name, delivery_city_name, max_routes=5):
        """
        Predlaže najbolje rute između dva grada
        
        Args:
            pickup_city_name: Naziv grada preuzimanja
            delivery_city_name: Naziv grada dostave
            max_routes: Maksimalan broj predloženih ruta
            
        Returns:
            List[dict]: Lista predloženih ruta sa detaljima
        """
        try:
            pickup_city = City.objects.get(name=pickup_city_name)
            delivery_city = City.objects.get(name=delivery_city_name)
        except City.DoesNotExist:
            return []
        
        # Pronađi direktne puteve
        direct_routes = cls._find_direct_routes(pickup_city, delivery_city)
        
        # Pronađi rute sa presedanjem
        indirect_routes = cls._find_indirect_routes(pickup_city, delivery_city)
        
        # Kombinuj i sortiraj rute
        all_routes = direct_routes + indirect_routes
        
        # Sortiraj po prioritetu i rastojanju
        sorted_routes = sorted(all_routes, key=lambda x: (x['priority'], x['total_distance']))
        
        return sorted_routes[:max_routes]
    
    @classmethod
    def _find_direct_routes(cls, pickup_city, delivery_city):
        """Pronalazi direktne rute između dva grada"""
        routes = []
        
        # Pronađi puteve koji direktno povezuju gradove
        highways = Highway.objects.filter(
            Q(start_city=pickup_city, end_city=delivery_city) |
            Q(start_city=delivery_city, end_city=pickup_city)
        ).order_by('priority')
        
        for highway in highways:
            route_data = {
                'name': f"Direktna ruta: {highway.name}",
                'highways': [highway],
                'total_distance': float(highway.distance_km or 0),
                'estimated_time_hours': cls._calculate_travel_time(highway.distance_km, highway.highway_type),
                'toll_cost': cls._calculate_toll_cost([highway]),
                'fuel_cost_estimate': cls._calculate_fuel_cost(highway.distance_km),
                'priority': highway.priority,
                'route_type': 'direct',
                'description': f"{highway.get_highway_type_display()} - {highway.description}"
            }
            routes.append(route_data)
        
        return routes
    
    @classmethod
    def _find_indirect_routes(cls, pickup_city, delivery_city):
        """Pronalazi rute sa jednim presedanjem kroz veće gradove"""
        routes = []
        
        # Glavni gradovi kroz koje se može ići
        major_cities = City.objects.filter(is_major=True).exclude(
            id__in=[pickup_city.id, delivery_city.id]
        )
        
        for transit_city in major_cities:
            # Ruta: pickup -> transit -> delivery
            first_leg = Highway.objects.filter(
                Q(start_city=pickup_city, end_city=transit_city) |
                Q(start_city=transit_city, end_city=pickup_city)
            ).order_by('priority').first()
            
            second_leg = Highway.objects.filter(
                Q(start_city=transit_city, end_city=delivery_city) |
                Q(start_city=delivery_city, end_city=transit_city)
            ).order_by('priority').first()
            
            if first_leg and second_leg:
                highways = [first_leg, second_leg]
                total_distance = (first_leg.distance_km or 0) + (second_leg.distance_km or 0)
                
                route_data = {
                    'name': f"Ruta preko {transit_city.name}",
                    'highways': highways,
                    'total_distance': float(total_distance),
                    'estimated_time_hours': cls._calculate_travel_time(total_distance, 'mixed'),
                    'toll_cost': cls._calculate_toll_cost(highways),
                    'fuel_cost_estimate': cls._calculate_fuel_cost(total_distance),
                    'priority': max(first_leg.priority, second_leg.priority),
                    'route_type': 'indirect',
                    'transit_city': transit_city.name,
                    'description': f"Preko {transit_city.name} - {first_leg.get_highway_type_display()} + {second_leg.get_highway_type_display()}"
                }
                routes.append(route_data)
        
        return routes
    
    @classmethod
    def _calculate_travel_time(cls, distance_km, highway_type):
        """Izračunava vreme putovanja na osnovu tipa puta"""
        if not distance_km:
            return 0
        
        # Prosečne brzine po tipu puta (km/h)
        speed_map = {
            'highway': 90,      # Autoput
            'main_road': 70,    # Magistralni put
            'regional': 60,     # Regionalni put
            'local': 50,        # Lokalni put
            'mixed': 75         # Mešovito
        }
        
        speed = speed_map.get(highway_type, 70)
        return round(float(distance_km) / speed, 1)
    
    @classmethod
    def _calculate_toll_cost(cls, highways):
        """Izračunava troškove putarine"""
        toll_cost = Decimal('0.0')
        
        for highway in highways:
            if highway.toll_road:
                # Osnovna putarina: 5 RSD po kilometru za autoput
                if highway.highway_type == 'highway':
                    toll_cost += (highway.distance_km or 0) * Decimal('5.0')
                else:
                    toll_cost += (highway.distance_km or 0) * Decimal('2.0')
        
        return float(toll_cost)
    
    @classmethod
    def _calculate_fuel_cost(cls, distance_km):
        """Izračunava troškove goriva"""
        if not distance_km:
            return 0.0
        
        # Prosečna potrošnja: 35L/100km, cena dizela: 170 RSD/L
        fuel_consumption_per_100km = 35
        diesel_price_per_liter = Decimal('170.0')
        
        fuel_needed = (distance_km * fuel_consumption_per_100km) / 100
        fuel_cost = fuel_needed * diesel_price_per_liter
        
        return float(fuel_cost)
    
    @classmethod
    def create_routes_for_shipment(cls, shipment):
        """
        Kreira predložene rute za konkretnu pošiljku
        """
        if not shipment.pickup_city or not shipment.delivery_city:
            return []
        
        suggested_routes = cls.suggest_routes(
            shipment.pickup_city, 
            shipment.delivery_city
        )
        
        # Obriši postojeće rute za ovu pošiljku
        Route.objects.filter(shipment=shipment).delete()
        
        created_routes = []
        
        for i, route_data in enumerate(suggested_routes):
            # Kreiraj Route objekat
            route = Route.objects.create(
                shipment=shipment,
                name=route_data['name'],
                total_distance=Decimal(str(route_data['total_distance'])),
                toll_cost=Decimal(str(route_data['toll_cost'])),
                fuel_cost_estimate=Decimal(str(route_data['fuel_cost_estimate'])),
                is_recommended=(i == 0),  # Prva ruta je preporučena
                priority=i + 1
            )
            
            # Dodaj puteve u rutu
            for order, highway in enumerate(route_data['highways']):
                RouteHighway.objects.create(
                    route=route,
                    highway=highway,
                    order=order + 1
                )
            
            created_routes.append(route)
        
        return created_routes


class DriverMatchingEngine:
    """
    Algoritam za pronalaženje najbližih vozača
    """
    
    @classmethod
    def find_nearby_drivers(cls, shipment, radius_km=50):
        """
        Pronalazi vozače u blizini rute pošiljke
        
        Args:
            shipment: Shipment objekat
            radius_km: Radijus pretrage u kilometrima
            
        Returns:
            QuerySet: Vozači sortirani po udaljenosti
        """
        # Pronađi vozače koji imaju aktivna vozila
        from django.contrib.auth.models import User
        
        carriers = User.objects.filter(
            profile__user_type='carrier',
            vehicles__is_active=True
        ).distinct()
        
        # TODO: Implementirati geolokaciju kada bude dostupna
        # Za sada vraćamo sve aktivne vozače
        
        return carriers
    
    @classmethod
    def match_vehicle_to_shipment(cls, shipment):
        """
        Pronalazi vozila koja mogu da prevoze pošiljku
        """
        suitable_vehicles = Vehicle.objects.filter(
            is_active=True,
            max_weight__gte=shipment.weight,
            max_volume__gte=shipment.volume or 0
        )
        
        return suitable_vehicles
    
    @classmethod
    def calculate_compatibility_score(cls, shipment, vehicle):
        """
        Izračunava ocenu kompatibilnosti između pošiljke i vozila
        """
        score = 100
        
        # Penalizuj prekapacitet
        if vehicle.max_weight:
            weight_ratio = float(shipment.weight) / float(vehicle.max_weight)
            if weight_ratio > 0.9:
                score += 20  # Bonus za dobro iskorišćenje
            elif weight_ratio < 0.3:
                score -= 30  # Penalizacija za loše iskorišćenje
        
        # Tip vozila vs tip tereta
        if shipment.cargo_type == 'refrigerated' and 'hladnjača' not in vehicle.vehicle_type.lower():
            score -= 50
        
        if shipment.cargo_type == 'oversized' and vehicle.vehicle_type not in ['trailer', 'mega']:
            score -= 40
        
        return max(0, score)
