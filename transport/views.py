# transport/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm, OrderCreationForm
from .models import UserProfile, Order

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role=form.cleaned_data['role'])
            login(request, user)
            return redirect('order_list')
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
    # Provera uloge korisnika
    try:
        if request.user.profile.role == 'driver':
            pending_orders = Order.objects.filter(status='pending').order_by('-created_at')
            context = {'orders': pending_orders, 'is_driver': True}
        elif request.user.profile.role == 'client':
            # Ako je klijent, prikazi samo njegove narudzbine
            client_orders = Order.objects.filter(client=request.user).order_by('-created_at')
            context = {'orders': client_orders, 'is_driver': False}
        else: # Administrator
            pending_orders = Order.objects.all().order_by('-created_at')
            context = {'orders': pending_orders, 'is_driver': True} # Admin može da vidi sve
    except UserProfile.DoesNotExist:
        # Prikazuje praznu listu ako profil ne postoji
        context = {'orders': [], 'is_driver': False}

    return render(request, 'transport/order_list.html', context)

@login_required
def accept_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Provera da li je ulogovani korisnik vozač
    if request.user.profile.role != 'driver':
        messages.error(request, 'Samo vozači mogu da prihvate narudžbinu.')
        return redirect('order_list')

    # Provera da li je narudžbina na čekanju
    if order.status != 'pending':
        messages.error(request, 'Ova narudžbina je već prihvaćena ili otkazana.')
        return redirect('order_list')
    
    # Postavljanje vozača i statusa
    order.driver = request.user
    order.status = 'accepted'
    order.save()
    
    messages.success(request, 'Uspešno ste prihvatili narudžbinu!')
    return redirect('order_details', order_id=order.id)
