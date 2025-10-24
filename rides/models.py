from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator

class Ride(models.Model):
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('assigned', 'Assigned'),
        ('dropped', 'Dropped'),
    )

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rides_as_rider'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides_as_customer'
    )
    pickup_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    total_distance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.destination}"

class RideEvent(models.Model):
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='events'
    )
    step_count = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['step_count', 'created_at']

    def __str__(self):
        return f"Step {self.step_count}: {self.description}"
