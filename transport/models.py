from django.db import models
from django.contrib.auth.models import User

# PROFIL korisnika da čuva rolu (client/driver)
class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('driver', 'Driver'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Vozilo
class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20)
    model = models.CharField(max_length=50)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.model} ({self.plate_number})"


# Narudžbina / Order
class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.client.username}"
