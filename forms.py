# transport/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserProfile.USER_ROLES, label="Uloga")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('role',)
