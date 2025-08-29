from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Shipment, Vehicle, ShipmentOffer


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
        fields = ['vehicle_type', 'license_plate', 'capacity', 'volume']
        widgets = {
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registarske tablice'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Kapacitet u tonama'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Zapremina u m³'}),
        }
        labels = {
            'vehicle_type': 'Tip vozila',
            'license_plate': 'Registarske tablice',
            'capacity': 'Kapacitet (tone)',
            'volume': 'Zapremina (m³)',
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
