from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from decimal import Decimal


class BillingPlans(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField()
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    expiry_days = models.IntegerField(default=30)
    
    def __str__(self):
        return f"{self.name} | {self.price}"