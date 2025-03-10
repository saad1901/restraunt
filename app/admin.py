from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Table)
admin.site.register(MenuCategory)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItems)
admin.site.register(Hotel)
admin.site.register(User)

