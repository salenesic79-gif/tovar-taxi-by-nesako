# transport/models.py
from django.db import models
from django.contrib.auth.models import User

# Profil korisnika sa rolama
class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Vozila koja koriste vozači
class Vehicle(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'profile__role': 'driver'})
    make = models.CharField(max_length=100)   # marka (npr. Mercedes)
    model = models.CharField(max_length=100)  # model (npr. Sprinter)
    plate_number = models.CharField(max_length=20, unique=True)  # registracija
    capacity = models.IntegerField()  # kapacitet u kg ili m3

    def __str__(self):
        return f"{self.make} {self.model} - {self.plate_number}"


# Narudžbina transporta
class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    cargo_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.client.username}"
