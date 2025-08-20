from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Vehicle


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["start_location", "end_location", "vehicle"]   # ✅ sad su polja usklađena
        widgets = {
            "start_location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Polazna lokacija"}),
            "end_location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Odredište"}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["plate_number", "model"]
