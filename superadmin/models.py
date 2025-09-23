from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from decimal import Decimal


class BillingPlans(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.IntegerField()
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    # owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Assuming Django's built-in User model
    # owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # status = models.BooleanField(default=False)
    # agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent', blank=True, null=True)
    # ownername = models.CharField(max_length=255)
    # owneremail = models.EmailField(max_length=255)
    # ownerphone = models.CharField(max_length=15)