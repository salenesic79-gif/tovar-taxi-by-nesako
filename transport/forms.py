# transport/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Order, Vehicle # DODATO: import Vehicle

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES, label="Uloga")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('role',)

class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['start_location', 'end_location', 'item_type', 'item_weight', 'item_dimensions', 'proposed_price']
        widgets = {
            'start_location': forms.TextInput(attrs={'placeholder': 'Polazna lokacija'}),
            'end_location': forms.TextInput(attrs={'placeholder': 'Krajnja lokacija'}),
            'item_type': forms.TextInput(attrs={'placeholder': 'Npr. kutije, nameštaj, elektronika'}),
            'item_weight': forms.NumberInput(attrs={'placeholder': 'Težina u kg'}),
            'item_dimensions': forms.TextInput(attrs={'placeholder': 'Npr. 1m x 2m x 1.5m'}),
            'proposed_price': forms.NumberInput(attrs={'placeholder': 'Cena koju ste spremni da platite'}),
        }

# NOVA FORMA ZA DODAVANJE VOZILA
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['driver']
        widgets = {
            'license_plate': forms.TextInput(attrs={'placeholder': 'Registarske tablice'}),
            'description': forms.TextInput(attrs={'placeholder': 'Opis (npr. Iveco, Mercedes)'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Visina (m)'}),
            'width': forms.NumberInput(attrs={'placeholder': 'Širina (m)'}),
            'length': forms.NumberInput(attrs={'placeholder': 'Dužina (m)'}),
            'weight_capacity': forms.NumberInput(attrs={'placeholder': 'Nosivost (t)'}),
            'color': forms.TextInput(attrs={'placeholder': 'Boja vozila'}),
        }