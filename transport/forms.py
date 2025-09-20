from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Shipment, Vehicle, ShipmentOffer, Tour

class SignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ('naručilac', 'Naručilac transporta'),
        ('prevoznik', 'Prevoznik'),
        ('vozač', 'Vozač'),
    ]
    
    first_name = forms.CharField(max_length=30, required=True, label='Ime')
    last_name = forms.CharField(max_length=30, required=True, label='Prezime')
    email = forms.EmailField(required=True, label='Email')
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label='Tip korisnika')
    phone_number = forms.CharField(max_length=20, required=False, label='Telefon')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Adresa')
    company_name = forms.CharField(max_length=200, required=False, label='Naziv kompanije')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Korisničko ime'
        self.fields['password1'].label = 'Lozinka'
        self.fields['password2'].label = 'Potvrda lozinke'
        
        # Add CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            'title', 'description', 'pickup_address', 'pickup_city',
            'delivery_address', 'delivery_city', 'cargo_weight', 'cargo_volume',
            'cargo_type', 'pickup_date', 'delivery_date', 'budget'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Naziv pošiljke'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Opis tereta'}),
            'pickup_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresa preuzimanja'}),
            'pickup_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grad preuzimanja'}),
            'delivery_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresa dostave'}),
            'delivery_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Grad dostave'}),
            'cargo_weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Težina u tonama'}),
            'cargo_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Zapremina u m³'}),
            'cargo_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tip tereta'}),
            'pickup_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'delivery_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Budžet u RSD'}),
        }
        labels = {
            'title': 'Naziv pošiljke',
            'description': 'Opis tereta',
            'pickup_address': 'Adresa preuzimanja',
            'pickup_city': 'Grad preuzimanja',
            'delivery_address': 'Adresa dostave',
            'delivery_city': 'Grad dostave',
            'cargo_weight': 'Težina tereta (tone)',
            'cargo_volume': 'Zapremina tereta (m³)',
            'cargo_type': 'Tip tereta',
            'pickup_date': 'Datum preuzimanja',
            'delivery_date': 'Datum dostave',
            'budget': 'Budžet (RSD)',
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'vehicle_brand', 'vehicle_color', 'license_plate', 'transport_license', 'capacity', 'volume', 'loading_height']
        widgets = {
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_brand': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_color': forms.Select(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'BG 123-AB'}),
            'transport_license': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Broj dozvole za prevoz tereta'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Kapacitet u tonama'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Zapremina u m³'}),
            'loading_height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'npr. 250', 'min': '100', 'max': '400'}),
        }
        labels = {
            'vehicle_type': 'Tip vozila',
            'vehicle_brand': 'Marka vozila',
            'vehicle_color': 'Boja vozila',
            'license_plate': 'Registarski broj vozila',
            'transport_license': 'Broj dozvole za prevoz tereta',
            'capacity': 'Kapacitet (tone)',
            'volume': 'Zapremina (m³)',
            'loading_height': 'Visina utovarnog dela (cm)',
        }


class ShipmentOfferForm(forms.ModelForm):
    class Meta:
        model = ShipmentOffer
        fields = ['vehicle', 'price', 'message']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Cena u RSD'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Poruka naručiocu (opciono)'}),
        }
        labels = {
            'vehicle': 'Vozilo',
            'price': 'Cena (RSD)',
            'message': 'Poruka',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_available=True)


class TourForm(forms.ModelForm):
    CARGO_TYPE_CHOICES = [
        ('paleta', 'Paleta 120x80'),
        ('paketna_roba', 'Paketna roba'),
        ('paleta_paketna_roba', 'Paleta ili paketna roba'),
        ('rasuti_teret', 'Rasuti teret'),
        ('tečni_teret', 'Tečni teret'),
    ]
    
    ROUTE_CHOICES = [
        ('', 'Izaberite putanju'),
        ('a1_beograd_novi_sad', 'A1 - Beograd - Novi Sad'),
        ('a1_novi_sad_subotica', 'A1 - Novi Sad - Subotica'),
        ('a2_beograd_obrenovac', 'A2 - Beograd - Obrenovac'),
        ('a3_beograd_nis', 'A3 - Beograd - Niš'),
        ('a4_nis_dimitrovgrad', 'A4 - Niš - Dimitrovgrad'),
        ('m1_beograd_pancevo', 'M1 - Beograd - Pančevo'),
        ('m22_beograd_cacak', 'M22 - Beograd - Čačak'),
        ('ostalo', 'Ostala putanja'),
    ]
    
    polaziste = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Unesite polazište',
            'id': 'polaziste'
        }),
        label='Polazište'
    )
    
    odrediste = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Unesite odredište'
        }),
        label='Odredište'
    )
    
    planirana_putanja = forms.ChoiceField(
        choices=ROUTE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Planirana putanja'
    )
    
    dostupno_za_dotovar = forms.ChoiceField(
        choices=CARGO_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Dostupno za dotovar'
    )
    
    kapacitet = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kapacitet',
            'step': '0.01'
        }),
        label='Kapacitet (tone)'
    )
    
    slobodna_kilaza = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Slobodna kilaža',
            'step': '0.01'
        }),
        label='Slobodna kilaža (kg)'
    )
    
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        widget=forms.HiddenInput(),
        required=False
    )
    
    class Meta:
        model = Tour
        fields = ['polaziste', 'odrediste', 'planirana_putanja', 'dostupno_za_dotovar', 'kapacitet', 'slobodna_kilaza']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        vehicle_license = kwargs.pop('vehicle_license', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_available=True)
            
        if vehicle_license and user:
            try:
                vehicle = Vehicle.objects.get(license_plate=vehicle_license, owner=user)
                self.fields['vehicle'].initial = vehicle
                # Popuni kapacitet na osnovu vozila
                self.fields['kapacitet'].initial = vehicle.capacity
            except Vehicle.DoesNotExist:
                pass
