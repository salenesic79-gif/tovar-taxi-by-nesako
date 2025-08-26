from django.db import models
from django.contrib.auth.models import User
import uuid

# Cargo type choices
CARGO_TYPES = [
    ('general', 'Opšti teret'),
    ('fragile', 'Krhki teret'),
    ('hazardous', 'Opasni teret'),
    ('refrigerated', 'Rashladni teret'),
    ('oversized', 'Nadgabaritni teret'),
]

class Profile(models.Model):
    USER_TYPES = [
        ('shipper', 'Naručilac transporta'),
        ('carrier', 'Prevoznik'),
        ('forwarder', 'Špediter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='shipper')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('van', 'Kombi'),
        ('truck', 'Kamion'),
        ('trailer', 'Šleper'),
        ('mega', 'Mega trailer'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    license_plate = models.CharField(max_length=20, unique=True)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Maksimalna nosivost u kg')
    max_volume = models.DecimalField(max_digits=8, decimal_places=2, help_text='Maksimalna zapremina u m³')
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.license_plate} - {self.get_vehicle_type_display()}"

class Shipment(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nacrt'),
        ('published', 'Objavljeno'),
        ('assigned', 'Dodeljeno'),
        ('in_transit', 'U transportu'),
        ('delivered', 'Isporučeno'),
        ('cancelled', 'Otkazano'),
    ]
    
    shipper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipments')
    carrier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_shipments')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Pickup location
    pickup_address = models.CharField(max_length=500, help_text='📍 Adresa preuzimanja')
    pickup_city = models.CharField(max_length=100)
    pickup_postal_code = models.CharField(max_length=20, blank=True)
    pickup_country = models.CharField(max_length=100, default='Srbija')
    pickup_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    pickup_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Delivery location
    delivery_address = models.CharField(max_length=500, help_text='🎯 Adresa dostave')
    delivery_city = models.CharField(max_length=100)
    delivery_postal_code = models.CharField(max_length=20, blank=True)
    delivery_country = models.CharField(max_length=100, default='Srbija')
    delivery_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    delivery_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Cargo details
    cargo_type = models.CharField(max_length=20, choices=CARGO_TYPES, default='general')
    cargo_description = models.TextField()
    weight = models.DecimalField(max_digits=8, decimal_places=2, help_text='Težina u kg')
    volume = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text='Zapremina u m³')
    
    # Dates
    pickup_date = models.DateTimeField()
    delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Ponuđena cena u RSD')
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional info
    special_requirements = models.TextField(blank=True, help_text='Posebni zahtevi')
    contact_person = models.CharField(max_length=200, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f"TT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference_number} - {self.pickup_city} → {self.delivery_city}"

class ShipmentOffer(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='offers')
    carrier = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    offered_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shipment', 'carrier'], name='unique_shipment_carrier_offer')
        ]
    
    def __str__(self):
        return f"Ponuda za {self.shipment.reference_number} - {self.offered_price} RSD"
