from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vehicle, Order, Profile

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('driver', 'Driver'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'plate_number', 'capacity', 'available']

class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['origin', 'destination', 'cargo_description', 'created_at', 'status', 'customer', 'vehicle']
