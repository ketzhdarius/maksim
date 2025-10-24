from django.db import models
from accounts.models import CustomUser
from django.core.validators import MinValueValidator

class Ride(models.Model):
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('dropped', 'Dropped'),
    )

    rider = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='rides_as_rider')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rides_as_customer')
    pickup_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    total_distance = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.destination}"

class RideEvent(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='events')
    step_count = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_count']

    def __str__(self):
        return f"Step {self.step_count}: {self.description}"
