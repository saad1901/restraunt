from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='waiterhome'),
    path('owner', views.owner, name='owner'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),

]
