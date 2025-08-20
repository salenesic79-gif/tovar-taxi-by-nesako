from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, A1  # ovde koristimo A1 umesto Vehicle

# Forma za kreiranje korisnika
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

# Forma za kreiranje narudžbine
class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "start_location",
            "end_location",
            "vehicle",  # polje u Order modelu sada treba da referencira A1
            "customer_name",
            "customer_phone",
        ]

# Forma za A1 model (ranije Vehicle)
class VehicleForm(forms.ModelForm):
    class Meta:
        model = A1
        fields = ["plate_number", "model"]
