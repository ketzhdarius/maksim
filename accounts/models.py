from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('rider', 'Rider'),
        ('staff', 'Staff'),
    )

    middle_name = models.CharField(max_length=150, blank=True)
    user_role = models.CharField(max_length=10, choices=USER_ROLES, default='customer')
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    def get_full_name(self):
        """Return the full name with middle name if available."""
        full_name = super().get_full_name()
        if self.middle_name:
            names = full_name.split()
            if len(names) >= 2:
                return f"{names[0]} {self.middle_name} {' '.join(names[1:])}"
        return full_name
