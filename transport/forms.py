from django import forms
from .models import Vehicle, Order

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'capacity', 'status']

class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['origin', 'destination', 'cargo_description', 'status']
