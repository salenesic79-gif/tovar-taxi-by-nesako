# transport/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            login(request, user)
            return redirect('login') # Privremeno preusmeravanje na stranicu za logovanje
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'transport/register.html', {'form': form})
