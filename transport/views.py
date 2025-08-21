from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, OrderCreationForm, VehicleForm
from .models import Order, Vehicle, Profile

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
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = request.user.profile
            vehicle.save()
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'transport/vehicle_create.html', {'form': form})

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(driver=request.user.profile)
    return render(request, 'transport/vehicle_list.html', {'vehicles': vehicles})

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderCreationForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user.profile
            order.save()
            return redirect('order_list')
    else:
        form = OrderCreationForm()
    return render(request, 'transport/order_create.html', {'form': form})

@login_required
def order_list(request):
    orders = Order.objects.filter(customer=request.user.profile)
    return render(request, 'transport/order_list.html', {'orders': orders})
