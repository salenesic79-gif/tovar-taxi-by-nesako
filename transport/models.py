from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_ROLES = (
        ('client', 'Poručilac'),
        ('driver', 'Vozač/prevoznik'),
        ('admin', 'Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='client')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_driver_validated = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

class Vehicle(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles')

    license_plate = models.CharField(max_length=20, unique=True, verbose_name="Registarske tablice")
    description = models.CharField(max_length=255, verbose_name="Opis (npr. Iveco, Mercedes)", blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Visina (m)")
    width = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Širina (m)")
    length = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Dužina (m)")
    weight_capacity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Nosivost (t)")
    color = models.CharField(max_length=50, blank=True, verbose_name="Boja vozila")

    def __str__(self):
        return f'Vozilo {self.license_plate} - {self.description}'

class Order(models.Model):
    STATUSES = (
        ('pending', 'Na čekanju'),
        ('accepted', 'Prihvaćena'),
        ('in_progress', 'U toku'),
        ('delivered', 'Isporučena'),
        ('cancelled', 'Otkazana'),
    )
    
    is_loaded = models.BooleanField(default=False) 

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_orders')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_orders')
    
    accepted_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_orders')

    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    
    item_type = models.CharField(max_length=100)
    item_weight = models.DecimalField(max_digits=10, decimal_places=2)
    item_dimensions = models.CharField(max_length=100)
    
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Narudžbina #{self.id} od {self.client.username}'
