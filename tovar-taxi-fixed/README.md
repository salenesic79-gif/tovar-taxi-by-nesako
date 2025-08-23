# Tovar Taxi - Logistička Aplikacija

Moderna Django aplikacija za upravljanje logističkim uslugama.

## Instalacija

1. Kloniraj repozitorijum:
```bash
git clone https://github.com/salenesic79-gif/tovar-taxi-by-nesako.git
cd tovar-taxi-by-nesako
```

2. Kreiraj virtuelno okruženje:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Instaliraj zavisnosti:
```bash
pip install -r requirements.txt
```

4. Pokreni migracije:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Kreiraj superuser (opciono):
```bash
python manage.py createsuperuser
```

6. Pokreni server:
```bash
python manage.py runserver
```

## Funkcionalnosti

- ✅ Registracija i prijava korisnika
- ✅ Prošireni profil korisnika (telefon, adresa)
- ✅ Moderni Bootstrap UI
- ✅ Responsive dizajn
- ✅ Srpski jezik

## Struktura Projekta

```
tovar_taxi/
├── transport/          # Glavna aplikacija
│   ├── models.py      # Profile model
│   ├── views.py       # View funkcije
│   ├── forms.py       # Registracioni form
│   └── urls.py        # URL routing
├── templates/         # HTML template fajlovi
├── static/           # CSS, JS, slike
└── manage.py         # Django management
```

## Tehnologije

- Django 4.2+
- Bootstrap 5
- SQLite baza podataka
- Python 3.8+
