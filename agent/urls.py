from django.urls import path
from .views import *

urlpatterns = [
    path('home/', agenthome, name='agenthome'),  
]