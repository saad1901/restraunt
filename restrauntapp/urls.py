from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='waiterhome'),
    path('owner', views.owner, name='owner'),
    path('submit-order/', views.submit_order, name='submit_order'),
]
