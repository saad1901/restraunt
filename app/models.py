from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Hotel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    # owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Assuming Django's built-in User model
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent', blank=True, null=True)
    # ownername = models.CharField(max_length=255)
    # owneremail = models.EmailField(max_length=255)
    # ownerphone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'SuperAdmin'),
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('owner', 'Owner'),
        ('staff', 'Staff'),
    ]
    hint = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    staffof = models.ForeignKey(Hotel, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f"{self.username}"

class Table(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link table to hotel
    name = models.CharField(max_length=100)
    occupied = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link category to hotel
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link item to hotel
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link order to hotel
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    completedby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return f"Order {self.id} - {self.hotel.name}"

class OrderItems(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link order items to hotel
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    quantity = models.IntegerField(default=1)


