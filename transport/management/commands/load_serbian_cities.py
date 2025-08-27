from django.core.management.base import BaseCommand
from transport.models import City, Highway

class Command(BaseCommand):
    help = 'Load Serbian cities and highways data'

    def handle(self, *args, **options):
        self.stdout.write('Loading Serbian cities...')
        
        # Major cities with postal codes and regions
        cities_data = [
            # Belgrade region
            {'name': 'Beograd', 'postal_code': '11000', 'region': 'Grad Beograd', 'district': 'Grad Beograd', 'population': 1378682, 'is_major': True},
            {'name': 'Zemun', 'postal_code': '11080', 'region': 'Grad Beograd', 'district': 'Grad Beograd', 'population': 168170, 'is_major': True},
            {'name': 'Novi Beograd', 'postal_code': '11070', 'region': 'Grad Beograd', 'district': 'Grad Beograd', 'population': 214506, 'is_major': True},
            
            # Vojvodina
            {'name': 'Novi Sad', 'postal_code': '21000', 'region': 'Vojvodina', 'district': 'Južnobački okrug', 'population': 341625, 'is_major': True},
            {'name': 'Subotica', 'postal_code': '24000', 'region': 'Vojvodina', 'district': 'Severnobanatski okrug', 'population': 105681, 'is_major': True},
            {'name': 'Zrenjanin', 'postal_code': '23000', 'region': 'Vojvodina', 'district': 'Srednjebanatski okrug', 'population': 76511, 'is_major': True},
            {'name': 'Pančevo', 'postal_code': '26000', 'region': 'Vojvodina', 'district': 'Južnobanatski okrug', 'population': 76203, 'is_major': True},
            {'name': 'Kikinda', 'postal_code': '23300', 'region': 'Vojvodina', 'district': 'Severnobanatski okrug', 'population': 38065, 'is_major': False},
            {'name': 'Sombor', 'postal_code': '25000', 'region': 'Vojvodina', 'district': 'Zapadnobački okrug', 'population': 47623, 'is_major': False},
            {'name': 'Vršac', 'postal_code': '26300', 'region': 'Vojvodina', 'district': 'Južnobanatski okrug', 'population': 36040, 'is_major': False},
            {'name': 'Ruma', 'postal_code': '22400', 'region': 'Vojvodina', 'district': 'Sremski okrug', 'population': 30076, 'is_major': False},
            {'name': 'Inđija', 'postal_code': '22320', 'region': 'Vojvodina', 'district': 'Sremski okrug', 'population': 26025, 'is_major': False},
            {'name': 'Stara Pazova', 'postal_code': '22300', 'region': 'Vojvodina', 'district': 'Sremski okrug', 'population': 18602, 'is_major': False},
            
            # Central Serbia
            {'name': 'Niš', 'postal_code': '18000', 'region': 'Centralna Srbija', 'district': 'Nišavski okrug', 'population': 260237, 'is_major': True},
            {'name': 'Kragujevac', 'postal_code': '34000', 'region': 'Centralna Srbija', 'district': 'Šumadijski okrug', 'population': 179417, 'is_major': True},
            {'name': 'Čačak', 'postal_code': '32000', 'region': 'Centralna Srbija', 'district': 'Moravički okrug', 'population': 73331, 'is_major': True},
            {'name': 'Kraljevo', 'postal_code': '36000', 'region': 'Centralna Srbija', 'district': 'Raški okrug', 'population': 68749, 'is_major': True},
            {'name': 'Smederevo', 'postal_code': '11300', 'region': 'Centralna Srbija', 'district': 'Podunavski okrug', 'population': 64175, 'is_major': False},
            {'name': 'Leskovac', 'postal_code': '16000', 'region': 'Centralna Srbija', 'district': 'Jablanički okrug', 'population': 60288, 'is_major': False},
            {'name': 'Valjevo', 'postal_code': '14000', 'region': 'Centralna Srbija', 'district': 'Kolubarski okrug', 'population': 59073, 'is_major': False},
            {'name': 'Užice', 'postal_code': '31000', 'region': 'Centralna Srbija', 'district': 'Zlatibor', 'population': 52199, 'is_major': False},
            {'name': 'Vranje', 'postal_code': '17500', 'region': 'Centralna Srbija', 'district': 'Pčinjski okrug', 'population': 55138, 'is_major': False},
            {'name': 'Zaječar', 'postal_code': '19000', 'region': 'Centralna Srbija', 'district': 'Zaječarski okrug', 'population': 38165, 'is_major': False},
            {'name': 'Šabac', 'postal_code': '15000', 'region': 'Centralna Srbija', 'district': 'Mačvanski okrug', 'population': 53919, 'is_major': False},
            {'name': 'Požarevac', 'postal_code': '12000', 'region': 'Centralna Srbija', 'district': 'Braničevski okrug', 'population': 44183, 'is_major': False},
            {'name': 'Pirot', 'postal_code': '18300', 'region': 'Centralna Srbija', 'district': 'Pirotski okrug', 'population': 38785, 'is_major': False},
            {'name': 'Jagodina', 'postal_code': '35000', 'region': 'Centralna Srbija', 'district': 'Pomoravski okrug', 'population': 43311, 'is_major': False},
            {'name': 'Paraćin', 'postal_code': '35250', 'region': 'Centralna Srbija', 'district': 'Pomoravski okrug', 'population': 24573, 'is_major': False},
            {'name': 'Ćuprija', 'postal_code': '35230', 'region': 'Centralna Srbija', 'district': 'Pomoravski okrug', 'population': 19380, 'is_major': False},
            {'name': 'Smederevska Palanka', 'postal_code': '11420', 'region': 'Centralna Srbija', 'district': 'Podunavski okrug', 'population': 26795, 'is_major': False},
            {'name': 'Aranđelovac', 'postal_code': '34300', 'region': 'Centralna Srbija', 'district': 'Šumadijski okrug', 'population': 24797, 'is_major': False},
            {'name': 'Mladenovac', 'postal_code': '11400', 'region': 'Centralna Srbija', 'district': 'Grad Beograd', 'population': 22148, 'is_major': False},
            
            # Kosovo region (administrative)
            {'name': 'Kosovska Mitrovica', 'postal_code': '38220', 'region': 'Kosovo i Metohija', 'district': 'Kosovskomitrovski okrug', 'population': 40000, 'is_major': False},
            {'name': 'Prizren', 'postal_code': '20000', 'region': 'Kosovo i Metohija', 'district': 'Prizrenski okrug', 'population': 85000, 'is_major': False},
            {'name': 'Peć', 'postal_code': '30000', 'region': 'Kosovo i Metohija', 'district': 'Pećki okrug', 'population': 48000, 'is_major': False},
            
            # Additional important cities
            {'name': 'Loznica', 'postal_code': '15300', 'region': 'Centralna Srbija', 'district': 'Mačvanski okrug', 'population': 19351, 'is_major': False},
            {'name': 'Bor', 'postal_code': '19210', 'region': 'Centralna Srbija', 'district': 'Borski okrug', 'population': 34160, 'is_major': False},
            {'name': 'Negotin', 'postal_code': '19300', 'region': 'Centralna Srbija', 'district': 'Borski okrug', 'population': 16716, 'is_major': False},
            {'name': 'Novi Pazar', 'postal_code': '36300', 'region': 'Centralna Srbija', 'district': 'Raški okrug', 'population': 66527, 'is_major': False},
            {'name': 'Sjenica', 'postal_code': '36310', 'region': 'Centralna Srbija', 'district': 'Zlatibor', 'population': 14060, 'is_major': False},
            {'name': 'Priboj', 'postal_code': '31330', 'region': 'Centralna Srbija', 'district': 'Zlatibor', 'population': 14015, 'is_major': False},
            {'name': 'Ivanjica', 'postal_code': '32250', 'region': 'Centralna Srbija', 'district': 'Moravički okrug', 'population': 11810, 'is_major': False},
            {'name': 'Arilje', 'postal_code': '31230', 'region': 'Centralna Srbija', 'district': 'Zlatibor', 'population': 6762, 'is_major': False},
            {'name': 'Čajetina', 'postal_code': '31250', 'region': 'Centralna Srbija', 'district': 'Zlatibor', 'population': 2743, 'is_major': False},
        ]
        
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                postal_code=city_data['postal_code'],
                defaults=city_data
            )
            if created:
                self.stdout.write(f'Created city: {city.name}')
        
        self.stdout.write('Loading Serbian highways...')
        
        # Get cities for highway connections
        try:
            beograd = City.objects.get(name='Beograd')
            novi_sad = City.objects.get(name='Novi Sad')
            nis = City.objects.get(name='Niš')
            kragujevac = City.objects.get(name='Kragujevac')
            subotica = City.objects.get(name='Subotica')
            cacak = City.objects.get(name='Čačak')
            kraljevo = City.objects.get(name='Kraljevo')
            uzice = City.objects.get(name='Užice')
            leskovac = City.objects.get(name='Leskovac')
            vranje = City.objects.get(name='Vranje')
            sabac = City.objects.get(name='Šabac')
            valjevo = City.objects.get(name='Valjevo')
            smederevo = City.objects.get(name='Smederevo')
            pancevo = City.objects.get(name='Pančevo')
            zrenjanin = City.objects.get(name='Zrenjanin')
            
            highways_data = [
                # Autoputevi (A1, A2, A3, A4, A5)
                {'name': 'Autoput Beograd-Novi Sad', 'code': 'A1', 'highway_type': 'highway', 'start_city': beograd, 'end_city': novi_sad, 'distance_km': 94.0, 'toll_road': True, 'priority': 1},
                {'name': 'Autoput Beograd-Niš', 'code': 'A1', 'highway_type': 'highway', 'start_city': beograd, 'end_city': nis, 'distance_km': 237.0, 'toll_road': True, 'priority': 1},
                {'name': 'Autoput Novi Sad-Subotica', 'code': 'A1', 'highway_type': 'highway', 'start_city': novi_sad, 'end_city': subotica, 'distance_km': 108.0, 'toll_road': True, 'priority': 1},
                {'name': 'Autoput Beograd-Zagreb', 'code': 'A3', 'highway_type': 'highway', 'start_city': beograd, 'end_city': sabac, 'distance_km': 61.0, 'toll_road': True, 'priority': 1},
                {'name': 'Autoput Niš-Merdare', 'code': 'A1', 'highway_type': 'highway', 'start_city': nis, 'end_city': leskovac, 'distance_km': 45.0, 'toll_road': True, 'priority': 1},
                
                # Magistralni putevi (M1, M2, M3, itd.)
                {'name': 'Magistralni put M1', 'code': 'M1', 'highway_type': 'main_road', 'start_city': beograd, 'end_city': nis, 'distance_km': 250.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M1.1', 'code': 'M1.1', 'highway_type': 'main_road', 'start_city': beograd, 'end_city': novi_sad, 'distance_km': 95.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M2', 'code': 'M2', 'highway_type': 'main_road', 'start_city': beograd, 'end_city': valjevo, 'distance_km': 96.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M3', 'code': 'M3', 'highway_type': 'main_road', 'start_city': beograd, 'end_city': smederevo, 'distance_km': 46.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M4', 'code': 'M4', 'highway_type': 'main_road', 'start_city': novi_sad, 'end_city': zrenjanin, 'distance_km': 67.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M5', 'code': 'M5', 'highway_type': 'main_road', 'start_city': kragujevac, 'end_city': cacak, 'distance_km': 65.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M6', 'code': 'M6', 'highway_type': 'main_road', 'start_city': cacak, 'end_city': uzice, 'distance_km': 58.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M7', 'code': 'M7', 'highway_type': 'main_road', 'start_city': nis, 'end_city': vranje, 'distance_km': 73.0, 'toll_road': False, 'priority': 2},
                {'name': 'Magistralni put M8', 'code': 'M8', 'highway_type': 'main_road', 'start_city': kraljevo, 'end_city': uzice, 'distance_km': 74.0, 'toll_road': False, 'priority': 2},
                
                # Regionalni putevi (R1, R2, itd.)
                {'name': 'Regionalni put R1', 'code': 'R1', 'highway_type': 'regional', 'start_city': beograd, 'end_city': pancevo, 'distance_km': 18.0, 'toll_road': False, 'priority': 3},
                {'name': 'Regionalni put R2', 'code': 'R2', 'highway_type': 'regional', 'start_city': novi_sad, 'end_city': subotica, 'distance_km': 105.0, 'toll_road': False, 'priority': 3},
                {'name': 'Regionalni put R3', 'code': 'R3', 'highway_type': 'regional', 'start_city': kragujevac, 'end_city': kraljevo, 'distance_km': 75.0, 'toll_road': False, 'priority': 3},
                {'name': 'Regionalni put R4', 'code': 'R4', 'highway_type': 'regional', 'start_city': valjevo, 'end_city': uzice, 'distance_km': 85.0, 'toll_road': False, 'priority': 3},
                {'name': 'Regionalni put R5', 'code': 'R5', 'highway_type': 'regional', 'start_city': leskovac, 'end_city': vranje, 'distance_km': 45.0, 'toll_road': False, 'priority': 3},
            ]
            
            for highway_data in highways_data:
                highway, created = Highway.objects.get_or_create(
                    code=highway_data['code'],
                    start_city=highway_data['start_city'],
                    end_city=highway_data['end_city'],
                    defaults=highway_data
                )
                if created:
                    self.stdout.write(f'Created highway: {highway.code} - {highway.name}')
                    
        except City.DoesNotExist as e:
            self.stdout.write(f'Error: City not found - {e}')
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded Serbian cities and highways!'))
