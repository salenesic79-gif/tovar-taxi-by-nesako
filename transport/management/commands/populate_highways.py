from django.core.management.base import BaseCommand
from transport.models import City, Highway

class Command(BaseCommand):
    help = 'Popunjava bazu puteva Srbije sa osnovnim rutama'

    def handle(self, *args, **options):
        # Prvo pronađi gradove
        try:
            beograd = City.objects.get(name='Beograd')
            novi_sad = City.objects.get(name='Novi Sad')
            nis = City.objects.get(name='Niš')
            kragujevac = City.objects.get(name='Kragujevac')
            subotica = City.objects.get(name='Subotica')
            pancevo = City.objects.get(name='Pančevo')
            zrenjanin = City.objects.get(name='Zrenjanin')
            cacak = City.objects.get(name='Čačak')
            kraljevo = City.objects.get(name='Kraljevo')
            uzice = City.objects.get(name='Užice')
            sabac = City.objects.get(name='Šabac')
            valjevo = City.objects.get(name='Valjevo')
            leskovac = City.objects.get(name='Leskovac')
            vranje = City.objects.get(name='Vranje')
            zajecar = City.objects.get(name='Zaječar')
            pirot = City.objects.get(name='Pirot')
        except City.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Grad nije pronađen: {e}'))
            return

        highways_data = [
            # Glavni autoputi
            {'name': 'Autoput A1 Beograd-Niš', 'code': 'A1', 'highway_type': 'highway', 
             'description': 'Glavni autoput sever-jug', 'start_city': beograd, 'end_city': nis, 
             'distance_km': 237.0, 'toll_road': True, 'priority': 1},
            
            {'name': 'Autoput A3 Beograd-Zagreb', 'code': 'A3', 'highway_type': 'highway',
             'description': 'Autoput prema Hrvatskoj', 'start_city': beograd, 'end_city': sabac,
             'distance_km': 95.0, 'toll_road': True, 'priority': 1},
            
            {'name': 'Autoput A4 Beograd-Južni Jadran', 'code': 'A4', 'highway_type': 'highway',
             'description': 'Autoput prema Crnoj Gori', 'start_city': beograd, 'end_city': uzice,
             'distance_km': 180.0, 'toll_road': True, 'priority': 1},
            
            # Magistralni putevi
            {'name': 'Magistrala M1 Beograd-Novi Sad', 'code': 'M1', 'highway_type': 'main_road',
             'description': 'Glavni put ka Vojvodini', 'start_city': beograd, 'end_city': novi_sad,
             'distance_km': 94.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M1.1 Novi Sad-Subotica', 'code': 'M1.1', 'highway_type': 'main_road',
             'description': 'Put ka mađarskoj granici', 'start_city': novi_sad, 'end_city': subotica,
             'distance_km': 108.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M24 Beograd-Pančevo', 'code': 'M24', 'highway_type': 'main_road',
             'description': 'Put ka Banatu', 'start_city': beograd, 'end_city': pancevo,
             'distance_km': 18.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M24.1 Pančevo-Zrenjanin', 'code': 'M24.1', 'highway_type': 'main_road',
             'description': 'Banatska magistrala', 'start_city': pancevo, 'end_city': zrenjanin,
             'distance_km': 45.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M5 Beograd-Kragujevac', 'code': 'M5', 'highway_type': 'main_road',
             'description': 'Šumadijska magistrala', 'start_city': beograd, 'end_city': kragujevac,
             'distance_km': 120.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M5.1 Kragujevac-Čačak', 'code': 'M5.1', 'highway_type': 'main_road',
             'description': 'Zapadna Morava', 'start_city': kragujevac, 'end_city': cacak,
             'distance_km': 65.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M5.2 Čačak-Kraljevo', 'code': 'M5.2', 'highway_type': 'main_road',
             'description': 'Dolina Zapadne Morave', 'start_city': cacak, 'end_city': kraljevo,
             'distance_km': 45.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M22 Beograd-Valjevo', 'code': 'M22', 'highway_type': 'main_road',
             'description': 'Put ka zapadnoj Srbiji', 'start_city': beograd, 'end_city': valjevo,
             'distance_km': 96.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M25 Niš-Leskovac', 'code': 'M25', 'highway_type': 'main_road',
             'description': 'Južna magistrala', 'start_city': nis, 'end_city': leskovac,
             'distance_km': 45.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M25.1 Leskovac-Vranje', 'code': 'M25.1', 'highway_type': 'main_road',
             'description': 'Put ka makedonskoj granici', 'start_city': leskovac, 'end_city': vranje,
             'distance_km': 65.0, 'toll_road': False, 'priority': 2},
            
            {'name': 'Magistrala M19 Niš-Zaječar', 'code': 'M19', 'highway_type': 'main_road',
             'description': 'Istočna magistrala', 'start_city': nis, 'end_city': zajecar,
             'distance_km': 110.0, 'toll_road': False, 'priority': 3},
            
            {'name': 'Magistrala M9 Niš-Pirot', 'code': 'M9', 'highway_type': 'main_road',
             'description': 'Put ka bugarskoj granici', 'start_city': nis, 'end_city': pirot,
             'distance_km': 75.0, 'toll_road': False, 'priority': 3},
            
            # Regionalni putevi
            {'name': 'Regionalni R101 Beograd-Smederevo', 'code': 'R101', 'highway_type': 'regional',
             'description': 'Podunavski put', 'start_city': beograd, 'end_city': City.objects.get(name='Smederevo'),
             'distance_km': 45.0, 'toll_road': False, 'priority': 3},
            
            {'name': 'Regionalni R102 Valjevo-Užice', 'code': 'R102', 'highway_type': 'regional',
             'description': 'Zapadni regionalni', 'start_city': valjevo, 'end_city': uzice,
             'distance_km': 85.0, 'toll_road': False, 'priority': 3},
        ]

        created_count = 0
        updated_count = 0

        for highway_data in highways_data:
            highway, created = Highway.objects.get_or_create(
                code=highway_data['code'],
                defaults=highway_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✅ Kreiran put: {highway}")
            else:
                # Ažuriraj postojeći put
                for key, value in highway_data.items():
                    setattr(highway, key, value)
                highway.save()
                updated_count += 1
                self.stdout.write(f"🔄 Ažuriran put: {highway}")

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🛣️ Završeno! Kreirano: {created_count}, Ažurirano: {updated_count} puteva'
            )
        )
