# transport/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, OrderCreationForm, VehicleForm
from django.contrib.auth import login
from .models import Order

def home(request):
    return render(request, 'home.html')

def user_signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.role = form.cleaned_data.get('role')
            user.profile.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderCreationForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            order.save()
            return redirect('order_list') # Preusmerite na stranicu sa listom narudžbina
    else:
        form = OrderCreationForm()
    return render(request, 'transport/order_create.html', {'form': form})
