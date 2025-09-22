from .views import owner_login, logout_user, redirection
from django.urls import path
from .setupView import *

urlpatterns = [
    path('login/', owner_login, name='owner_login'),
    path('', redirection, name='redirection'),
    path('logout/', logout_user, name='logout'),
    path('register/owner/', owner_register, name='owner_register'),
    path('register/hotel/', hotel_register, name='hotel_register'),
    path('register/', register, name='register')
]