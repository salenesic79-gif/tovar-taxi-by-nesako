from django import forms
from .models import Vehicle, Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('driver', 'Driver'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']


class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pickup_location', 'dropoff_location', 'scheduled_time']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'model']
