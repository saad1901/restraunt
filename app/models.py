from django.db import models

class Table(models.Model):
    name = models.CharField(max_length=100)
    occupied = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class MenuCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # attendedby = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    completed = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)  

class OrderItems(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class User(models.Model):
    pass    