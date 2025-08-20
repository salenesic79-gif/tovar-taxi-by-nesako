from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Order, Vehicle

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
        
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'description', 'height', 'width', 'length', 'weight_capacity', 'color']
        widgets = {
            'license_plate': forms.TextInput(attrs={'placeholder': 'Registarske tablice'}),
            'description': forms.TextInput(attrs={'placeholder': 'Npr. Iveco, Mercedes'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Visina u metrima'}),
            'width': forms.NumberInput(attrs={'placeholder': 'Širina u metrima'}),
            'length': forms.NumberInput(attrs={'placeholder': 'Dužina u metrima'}),
            'weight_capacity': forms.NumberInput(attrs={'placeholder': 'Nosivost u tonama'}),
            'color': forms.TextInput(attrs={'placeholder': 'Boja vozila'}),
        }
