from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order from {self.start_location} to {self.end_location}"

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    start_location = models.CharField(max_length=255)   # ✅ mora postojati
    end_location = models.CharField(max_length=255)     # ✅ mora postojati
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} from {self.start_location} to {self.end_location}"

class Vehicle(models.Model):
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.model} - {self.plate_number}"


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    start_location = models.CharField(max_length=255)   # ✅ dodato polje
    end_location = models.CharField(max_length=255)     # ✅ dodato polje
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} from {self.start_location} to {self.end_location}"
