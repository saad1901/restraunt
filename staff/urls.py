from django.urls import path
from .views import *

urlpatterns = [
    path('booking/', home, name='waiterhome'),
    path('waiter/orders/active/', waiter_active_orders, name='waiter_active_orders')
    ]