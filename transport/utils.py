from geopy.distance import geodesic
from .models import CenaPoKilometrazi


def izracunaj_cenu(broj_paleta, udaljenost_km):
    """Izračunava cenu na osnovu broja paleta i udaljenosti"""
    try:
        cena_obj = CenaPoKilometrazi.objects.get(broj_paleta=broj_paleta)
        
        if udaljenost_km <= 200:
            return float(cena_obj.cena_do_200km)
        else:
            return float(cena_obj.cena_preko_200km)
    except CenaPoKilometrazi.DoesNotExist:
        # Fallback cene ako nema u bazi
        if udaljenost_km <= 200:
            cene_do_200 = {1: 4000, 2: 6400, 3: 8400, 4: 10000, 5: 12000}
            return cene_do_200.get(broj_paleta, 0)
        else:
            cene_preko_200 = {1: 5500, 2: 9000, 3: 11850, 4: 14200, 5: 17000}
            return cene_preko_200.get(broj_paleta, 0)


def izracunaj_udaljenost(polazna_lat, polazna_lon, odredisna_lat, odredisna_lon):
    """Izračunava udaljenost između dve GPS koordinate u kilometrima"""
    polazna_koordinate = (polazna_lat, polazna_lon)
    odredisne_koordinate = (odredisna_lat, odredisna_lon)
    return geodesic(polazna_koordinate, odredisne_koordinate).kilometers


def predlozi_eko_ambalazu(tezina):
    """Predlaže eko-ambalažu na osnovu težine tereta"""
    
    if tezina <= 5:
        return "Biorazgradiva mala kutija (do 5kg) - preporučujemo kartonsku ambalažu od recikliranog materijala sa biorazgradivom zaštitom"
    elif tezina <= 20:
        return "Srednja reciklirana kutija (5-20kg) - koristi ojačanu kartonsku ambalažu sa zaštitnim materijalom od prirodnih vlakana"
    else:
        return "Velika kutija sa eko zaštitom (>20kg) - koristi drvenu paletu sa biorazgradivom folijom i prirodnim amortizacionim materijalom"


def kreiraj_osnovne_cene():
    """Kreira osnovne cene u bazi podataka"""
    osnovne_cene = [
        {'broj_paleta': 1, 'cena_do_200km': 4000, 'cena_preko_200km': 5500},
        {'broj_paleta': 2, 'cena_do_200km': 6400, 'cena_preko_200km': 9000},
        {'broj_paleta': 3, 'cena_do_200km': 8400, 'cena_preko_200km': 11850},
        {'broj_paleta': 4, 'cena_do_200km': 10000, 'cena_preko_200km': 14200},
        {'broj_paleta': 5, 'cena_do_200km': 12000, 'cena_preko_200km': 17000},
    ]
    
    for cena_data in osnovne_cene:
        CenaPoKilometrazi.objects.get_or_create(
            broj_paleta=cena_data['broj_paleta'],
            defaults={
                'cena_do_200km': cena_data['cena_do_200km'],
                'cena_preko_200km': cena_data['cena_preko_200km']
            }
        )


def izracunaj_cenu_za_prevoznika(cena_za_posiljaoce):
    """Izračunava cenu za prevoznika (minus 15% app fee)"""
    app_fee = cena_za_posiljaoce * 0.15
    cena_za_prevoznika = cena_za_posiljaoce - app_fee
    return cena_za_prevoznika, app_fee


# Alias for English function name used in test_mode_ngrok.py
create_base_prices = kreiraj_osnovne_cene
