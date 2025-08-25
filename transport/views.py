from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm

def signup_view(request):
    return render(request, 'transport/signup.html')

def signup_sender_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'transport/signup_sender.html', {'form': form})

def signup_carrier_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'transport/signup_carrier.html', {'form': form})

def home_view(request):
    return render(request, 'transport/home.html')

def settings_view(request):
    return render(request, 'transport/settings.html')
