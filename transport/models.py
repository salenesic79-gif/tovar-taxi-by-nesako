from django.db import models
from django.contrib.auth.models import User

class A1(models.Model):  # ranije Vehicle
    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.model} ({self.plate_number})"

class Order(models.Model):
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    vehicle = models.ForeignKey(A1, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} from {self.start_location} to {self.end_location}"
