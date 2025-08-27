from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Shipment, Vehicle, ShipmentOffer, Profile, City, Highway

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False, help_text='Broj telefona')
    address = forms.CharField(max_length=255, required=False, help_text='Adresa')
    company_name = forms.CharField(max_length=200, required=False, help_text='Naziv kompanije')
    tax_number = forms.CharField(max_length=50, required=False, help_text='PIB')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "phone_number", "address", "company_name", "tax_number")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', ''),
                company_name=self.cleaned_data.get('company_name', ''),
                tax_number=self.cleaned_data.get('tax_number', '')
            )
        return user

class ShipmentForm(forms.ModelForm):
    pickup_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        help_text='📍 Datum i vreme preuzimanja'
    )
    pickup_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        empty_label="Izaberite grad preuzimanja...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    pickup_region = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Oblast/Region preuzimanja'}))
    pickup_address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ulica i broj'}))
    pickup_postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poštanski broj'}))
    pickup_country = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Država'}))
    delivery_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        help_text='🎯 Datum i vreme dostave (opciono)'
    )
    delivery_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=False,
        empty_label="Izaberite grad dostave...",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    delivery_region = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Oblast/Region dostave'}))
    delivery_address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ulica i broj'}))
    delivery_postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poštanski broj'}))
    delivery_country = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Država'}))
    cargo_type = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tip tereta'}))
    cargo_description = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opis tereta...'}))
    weight = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'kg'}))
    volume = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'm³'}))
    offered_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'RSD'}))
    special_requirements = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Posebni zahtevi...'}))
    contact_person = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ime i prezime'}))
    contact_phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+381...'}))
    
    preferred_highways = forms.ModelMultipleChoiceField(
        queryset=Highway.objects.filter(priority__lte=3).order_by('priority', 'highway_type'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Izaberite željene puteve (opciono)'
    )

    class Meta:
        model = Shipment
        fields = [
            'pickup_address', 'pickup_city', 'pickup_region', 'pickup_postal_code', 'pickup_country',
            'delivery_address', 'delivery_city', 'delivery_region', 'delivery_postal_code', 'delivery_country',
            'cargo_type', 'cargo_description', 'weight', 'volume',
            'pickup_date', 'delivery_date', 'offered_price',
            'special_requirements', 'contact_person', 'contact_phone'
        ]
        widgets = {
            'pickup_address': forms.TextInput(attrs={'placeholder': '📍 Ulica i broj'}),
            'pickup_city': forms.TextInput(attrs={'placeholder': 'Grad'}),
            'delivery_address': forms.TextInput(attrs={'placeholder': '🎯 Ulica i broj'}),
            'delivery_city': forms.TextInput(attrs={'placeholder': 'Grad'}),
            'cargo_description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Opis tereta...'}),
            'weight': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'kg'}),
            'volume': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'm³'}),
            'offered_price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'RSD'}),
            'special_requirements': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Posebni zahtevi...'}),
            'contact_person': forms.TextInput(attrs={'placeholder': 'Ime i prezime'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': '+381...'})
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate', 'max_weight', 'max_volume', 'length', 'width', 'height']
        widgets = {
            'license_plate': forms.TextInput(attrs={'placeholder': 'BG-123-AB'}),
            'max_weight': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'kg'}),
            'max_volume': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'm³'}),
            'length': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'm'}),
            'width': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'm'}),
            'height': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'm'})
        }

class ShipmentOfferForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=user, is_active=True)

    class Meta:
        model = ShipmentOffer
        fields = ['vehicle', 'offered_price', 'message']
        widgets = {
            'offered_price': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'RSD'}),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Poruka pošaljiocu...'})
        }
