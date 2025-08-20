from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, OrderCreationForm, VehicleForm
from .models import Order

def home(request):
    # putanja ka template-u sa prefiksom aplikacije
    return render(request, 'transport/home.html')


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
            return redirect('order_list')
    else:
        form = OrderCreationForm()
    return render(request, 'transport/order_create.html', {'form': form})


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = VehicleForm()
    return render(request, 'transport/vehicle_create.html', {'form': form})
