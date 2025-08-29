from django.core.management.base import BaseCommand
from transport.models import City

class Command(BaseCommand):
    help = 'Popunjava bazu gradova Srbije sa poštanskim brojevima'

    def handle(self, *args, **options):
        cities_data = [
            # Beograd i okolina
            {'name': 'Beograd', 'postal_code': '11000', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 1378682, 'is_major': True},
            {'name': 'Zemun', 'postal_code': '11080', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 168170, 'is_major': True},
            {'name': 'Novi Beograd', 'postal_code': '11070', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 214506, 'is_major': True},
            {'name': 'Pančevo', 'postal_code': '26000', 'region': 'Južni Banat', 'district': 'Južnobanatski', 'population': 76203, 'is_major': True},
            {'name': 'Smederevo', 'postal_code': '11300', 'region': 'Podunavlje', 'district': 'Podunavski', 'population': 64175, 'is_major': True},
            
            # Vojvodina - Novi Sad i okolina
            {'name': 'Novi Sad', 'postal_code': '21000', 'region': 'Južna Bačka', 'district': 'Južnobački', 'population': 341625, 'is_major': True},
            {'name': 'Subotica', 'postal_code': '24000', 'region': 'Severna Bačka', 'district': 'Severnobački', 'population': 97910, 'is_major': True},
            {'name': 'Zrenjanin', 'postal_code': '23000', 'region': 'Srednji Banat', 'district': 'Srednjebanatski', 'population': 76511, 'is_major': True},
            {'name': 'Kikinda', 'postal_code': '23300', 'region': 'Severni Banat', 'district': 'Severnobanatski', 'population': 38065, 'is_major': True},
            {'name': 'Sombor', 'postal_code': '25000', 'region': 'Zapadna Bačka', 'district': 'Zapadnobački', 'population': 47623, 'is_major': True},
            {'name': 'Sremska Mitrovica', 'postal_code': '22000', 'region': 'Srem', 'district': 'Sremski', 'population': 37751, 'is_major': True},
            
            # Centralna Srbija - veći gradovi
            {'name': 'Niš', 'postal_code': '18000', 'region': 'Nišava', 'district': 'Nišavski', 'population': 260237, 'is_major': True},
            {'name': 'Kragujevac', 'postal_code': '34000', 'region': 'Šumadija', 'district': 'Šumadijski', 'population': 179417, 'is_major': True},
            {'name': 'Čačak', 'postal_code': '32000', 'region': 'Moravica', 'district': 'Moravički', 'population': 73331, 'is_major': True},
            {'name': 'Kraljevo', 'postal_code': '36000', 'region': 'Raška', 'district': 'Raški', 'population': 68749, 'is_major': True},
            {'name': 'Smederevska Palanka', 'postal_code': '11420', 'region': 'Podunavlje', 'district': 'Podunavski', 'population': 26795, 'is_major': True},
            {'name': 'Valjevo', 'postal_code': '14000', 'region': 'Kolubara', 'district': 'Kolubarski', 'population': 59073, 'is_major': True},
            {'name': 'Užice', 'postal_code': '31000', 'region': 'Zlatibor', 'district': 'Zlatiborski', 'population': 52199, 'is_major': True},
            {'name': 'Leskovac', 'postal_code': '16000', 'region': 'Jablanica', 'district': 'Jablanički', 'population': 60288, 'is_major': True},
            {'name': 'Vranje', 'postal_code': '17500', 'region': 'Pčinja', 'district': 'Pčinjski', 'population': 55138, 'is_major': True},
            {'name': 'Zaječar', 'postal_code': '19000', 'region': 'Zaječar', 'district': 'Zaječarski', 'population': 38165, 'is_major': True},
            {'name': 'Pirot', 'postal_code': '18300', 'region': 'Pirot', 'district': 'Pirotski', 'population': 38785, 'is_major': True},
            {'name': 'Jagodina', 'postal_code': '35000', 'region': 'Pomoravlje', 'district': 'Pomoravski', 'population': 43311, 'is_major': True},
            {'name': 'Paraćin', 'postal_code': '35250', 'region': 'Pomoravlje', 'district': 'Pomoravski', 'population': 24573, 'is_major': True},
            {'name': 'Ćuprija', 'postal_code': '35230', 'region': 'Pomoravlje', 'district': 'Pomoravski', 'population': 19380, 'is_major': True},
            {'name': 'Aranđelovac', 'postal_code': '34300', 'region': 'Šumadija', 'district': 'Šumadijski', 'population': 24797, 'is_major': True},
            {'name': 'Mladenovac', 'postal_code': '11400', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 22184, 'is_major': True},
            
            # Južna Srbija
            {'name': 'Prokuplje', 'postal_code': '18400', 'region': 'Toplica', 'district': 'Toplički', 'population': 27163, 'is_major': True},
            {'name': 'Kuršumlija', 'postal_code': '18430', 'region': 'Toplica', 'district': 'Toplički', 'population': 14149, 'is_major': False},
            {'name': 'Blace', 'postal_code': '18420', 'region': 'Toplica', 'district': 'Toplički', 'population': 11754, 'is_major': False},
            {'name': 'Vladičin Han', 'postal_code': '17510', 'region': 'Pčinja', 'district': 'Pčinjski', 'population': 8053, 'is_major': False},
            {'name': 'Surdulica', 'postal_code': '17520', 'region': 'Pčinja', 'district': 'Pčinjski', 'population': 10915, 'is_major': False},
            {'name': 'Bujanovac', 'postal_code': '17520', 'region': 'Pčinja', 'district': 'Pčinjski', 'population': 12011, 'is_major': False},
            
            # Zapadna Srbija
            {'name': 'Šabac', 'postal_code': '15000', 'region': 'Mačva', 'district': 'Mačvanski', 'population': 53919, 'is_major': True},
            {'name': 'Loznica', 'postal_code': '15300', 'region': 'Mačva', 'district': 'Mačvanski', 'population': 18714, 'is_major': True},
            {'name': 'Krupanj', 'postal_code': '15315', 'region': 'Mačva', 'district': 'Mačvanski', 'population': 4455, 'is_major': False},
            {'name': 'Ljubovija', 'postal_code': '15320', 'region': 'Mačva', 'district': 'Mačvanski', 'population': 3946, 'is_major': False},
            {'name': 'Mali Zvornik', 'postal_code': '15318', 'region': 'Mačva', 'district': 'Mačvanski', 'population': 4384, 'is_major': False},
            
            # Istočna Srbija
            {'name': 'Bor', 'postal_code': '19210', 'region': 'Bor', 'district': 'Borski', 'population': 34160, 'is_major': True},
            {'name': 'Majdanpek', 'postal_code': '19250', 'region': 'Bor', 'district': 'Borski', 'population': 7367, 'is_major': False},
            {'name': 'Negotin', 'postal_code': '19300', 'region': 'Bor', 'district': 'Borski', 'population': 16716, 'is_major': True},
            {'name': 'Kladovo', 'postal_code': '19320', 'region': 'Bor', 'district': 'Borski', 'population': 8913, 'is_major': False},
            
            # Dodatni gradovi po regionima
            {'name': 'Obrenovac', 'postal_code': '11500', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 24568, 'is_major': True},
            {'name': 'Lazarevac', 'postal_code': '11550', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 23551, 'is_major': True},
            {'name': 'Sopot', 'postal_code': '11460', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 3529, 'is_major': False},
            {'name': 'Barajevo', 'postal_code': '11351', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 9882, 'is_major': False},
            {'name': 'Grocka', 'postal_code': '11306', 'region': 'Grad Beograd', 'district': 'Beogradski', 'population': 10890, 'is_major': False},
            
            # Vojvodina - dodatni gradovi
            {'name': 'Vršac', 'postal_code': '26300', 'region': 'Južni Banat', 'district': 'Južnobanatski', 'population': 35701, 'is_major': True},
            {'name': 'Bela Crkva', 'postal_code': '26340', 'region': 'Južni Banat', 'district': 'Južnobanatski', 'population': 8868, 'is_major': False},
            {'name': 'Kovin', 'postal_code': '26220', 'region': 'Južni Banat', 'district': 'Južnobanatski', 'population': 13515, 'is_major': False},
            {'name': 'Opovo', 'postal_code': '26204', 'region': 'Južni Banat', 'district': 'Južnobanatski', 'population': 4527, 'is_major': False},
            {'name': 'Ruma', 'postal_code': '22400', 'region': 'Srem', 'district': 'Sremski', 'population': 30076, 'is_major': True},
            {'name': 'Inđija', 'postal_code': '22320', 'region': 'Srem', 'district': 'Sremski', 'population': 26025, 'is_major': True},
            {'name': 'Stara Pazova', 'postal_code': '22300', 'region': 'Srem', 'district': 'Sremski', 'population': 18602, 'is_major': True},
            {'name': 'Pećinci', 'postal_code': '22410', 'region': 'Srem', 'district': 'Sremski', 'population': 2399, 'is_major': False},
        ]

        created_count = 0
        updated_count = 0

        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                postal_code=city_data['postal_code'],
                defaults=city_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"✅ Kreiran grad: {city}")
            else:
                # Ažuriraj postojeći grad
                for key, value in city_data.items():
                    setattr(city, key, value)
                city.save()
                updated_count += 1
                self.stdout.write(f"🔄 Ažuriran grad: {city}")

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Završeno! Kreirano: {created_count}, Ažurirano: {updated_count} gradova'
            )
        )
