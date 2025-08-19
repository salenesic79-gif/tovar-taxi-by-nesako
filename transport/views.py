# transport/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, OrderCreationForm, VehicleForm
from .models import UserProfile, Order, Vehicle

def home(request):
    return render(request, 'transport/home.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'transport/register.html', {'form': form})

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderCreationForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = request.user
            order.save()
            return redirect('order_list')
    else:
        form = OrderCreationForm()
    
    return render(request, 'transport/create_order.html', {'form': form})

@login_required
def order_list(request):
    try:
        user_profile = request.user.profile
        if user_profile.role == 'driver':
            pending_orders = Order.objects.filter(status='pending').order_by('-created_at')
            context = {'orders': pending_orders, 'is_driver': True}
        else:
            client_orders = Order.objects.filter(client=request.user).order_by('-created_at')
            context = {'orders': client_orders, 'is_driver': False}
    except UserProfile.DoesNotExist:
        client_orders = Order.objects.filter(client=request.user).order_by('-created_at')
        context = {'orders': client_orders, 'is_driver': False}

    return render(request, 'transport/order_list.html', context)

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    try:
        if request.user.profile.role != 'driver':
            messages.error(request, 'Samo vozači mogu da prihvate narudžbinu.')
            return redirect('order_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Vaš nalog nema definisanu ulogu. Molimo kontaktirajte administratora.')
        return redirect('order_list')


    if order.status != 'pending':
        messages.error(request, 'Ova narudžbina je već prihvaćena ili otkazana.')
        return redirect('order_list')
    
    order.driver = request.user
    order.status = 'accepted'
    order.save()
    
    messages.success(request, 'Uspešno ste prihvatili narudžbinu!')
    return redirect('order_details', order_id=order.id)

@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    if request.user != order.client and (order.driver and request.user != order.driver):
        messages.error(request, 'Nemate pravo pristupa ovoj narudžbini.')
        return redirect('order_list')

    context = {
        'order': order,
    }
    
    return render(request, 'transport/order_details.html', context)

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = request.user
            vehicle.save()
            messages.success(request, 'Vozilo je uspešno dodato!')
            return redirect('add_vehicle')
    else:
        form = VehicleForm()
    
    context = {
        'form': form,
        'vehicles': request.user.vehicles.all()
    }
    return render(request, 'transport/add_vehicle.html', context)