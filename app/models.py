from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from decimal import Decimal


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
    active = models.BooleanField(default=True)
    food_type = models.CharField(max_length=10, blank=True, null=True)
    def __str__(self):
        return self.name

class Order(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link order to hotel
    table = models.ForeignKey(Table, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)
    started = models.BooleanField(default=False)  # Added field for cooking status
    phone_number = models.CharField(max_length=15, blank=True)
    completedby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    # New fields for order type and online source
    ORDER_TYPE_CHOICES = [
        ('table', 'Table'),
        ('online', 'Online'),
    ]
    ONLINE_SOURCE_CHOICES = [
        ('swiggy', 'Swiggy'),
        ('zomato', 'Zomato'),
        ('free', 'Free'),
        ('other', 'Other'),
    ]
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, default='table')
    online_source = models.CharField(max_length=10, choices=ONLINE_SOURCE_CHOICES, blank=True, null=True)

    def __str__(self):
        base = f"Order {self.id} - {self.hotel.name}"
        if self.order_type == 'online':
            return f"{base} (Online: {self.online_source})"
        return base

class OrderItems(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)  # Link order items to hotel
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='orderitems')
    quantity = models.IntegerField(default=1)


class PaymentDetails(models.Model):
    upiid = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('pcs', 'Pieces'),
        ('pkg', 'Packages'),
        ('box', 'Boxes'),
    ]
    
    STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES, default='pcs')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_stock')
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Automatically update status based on quantity and reorder level
        # Convert to Decimal objects for safe comparison
        qty = Decimal(str(self.quantity))
        zero = Decimal('0')
        reorder = Decimal(str(self.reorder_level))
        
        # Update status based on safe decimal comparisons
        if qty <= zero:
            self.status = 'out_of_stock'
        elif qty < reorder:
            self.status = 'low_stock'
        else:
            self.status = 'in_stock'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('usage', 'Usage'),
        ('adjustment', 'Adjustment'),
        ('writeoff', 'Write-off'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name} ({self.quantity})"
    
    class Meta:
        ordering = ['-transaction_date']
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
     