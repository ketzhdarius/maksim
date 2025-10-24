from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('rider', 'Rider'),
        ('staff', 'Staff'),
    )

    middle_name = models.CharField(max_length=150, blank=True)
    user_role = models.CharField(max_length=10, choices=USER_ROLES, default='customer')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_full_name(self):
        full_name = f"{self.first_name} {self.middle_name} {self.last_name}"
        return full_name.strip()

    def __str__(self):
        return self.get_full_name() or self.username
