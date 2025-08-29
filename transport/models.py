from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    ROLE_CHOICES = [
        ('naručilac', 'Naručilac transporta'),
        ('prevoznik', 'Prevoznik'),
        ('vozač', 'Vozač'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('kombi', 'Kombi'),
        ('kamion', 'Kamion'),
        ('šleper', 'Šleper'),
        ('mega_trailer', 'Mega trailer'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    license_plate = models.CharField(max_length=20, unique=True)
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Kapacitet u tonama")
    volume = models.DecimalField(max_digits=10, decimal_places=2, help_text="Zapremina u m³")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.license_plate} - {self.get_vehicle_type_display()}"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nacrt'),
        ('published', 'Objavljeno'),
        ('in_progress', 'U toku'),
        ('completed', 'Završeno'),
        ('cancelled', 'Otkazano'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_shipments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Lokacije
    pickup_address = models.CharField(max_length=300)
    delivery_address = models.CharField(max_length=300)
    pickup_city = models.CharField(max_length=100)
    delivery_city = models.CharField(max_length=100)
    
    # Teret
    cargo_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Težina u tonama")
    cargo_volume = models.DecimalField(max_digits=10, decimal_places=2, help_text="Zapremina u m³")
    cargo_type = models.CharField(max_length=100)
    
    # Cena i status
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Datumi
    pickup_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.pickup_city} → {self.delivery_city}"


class ShipmentOffer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Na čekanju'),
        ('accepted', 'Prihvaćena'),
        ('rejected', 'Odbijena'),
    ]
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='offers')
    carrier = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Ponuda za {self.shipment.title} - {self.price} RSD"


class Tour(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Potvrđena'),
        ('in_progress', 'U toku'),
        ('pickup_confirmed', 'Preuzeto'),
        ('delivered', 'Isporučeno'),
        ('completed', 'Završena'),
        ('cancelled', 'Otkazana'),
    ]
    
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE)
    offer = models.OneToOneField(ShipmentOffer, on_delete=models.CASCADE)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tours')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    pickup_confirmed_at = models.DateTimeField(null=True, blank=True)
    delivery_confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tura: {self.shipment.title}"


class ChatMessage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_offer', 'Nova ponuda'),
        ('offer_accepted', 'Ponuda prihvaćena'),
        ('offer_rejected', 'Ponuda odbijena'),
        ('tour_confirmed', 'Tura potvrđena'),
        ('pickup_confirmed', 'Preuzimanje potvrđeno'),
        ('delivery_confirmed', 'Isporuka potvrđena'),
        ('new_message', 'Nova poruka'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Opciono povezivanje sa objektima
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, null=True, blank=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Location(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lokacija za {self.tour} - {self.timestamp}"
