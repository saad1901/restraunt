from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='waiterhome'),
    path('owner', views.owner, name='owner'),
    path('settings', views.settings, name='settings'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),

    path('settings/categories/add/', views.add_category, name='add_category'),
    path('settings/categories/edit/', views.edit_category, name='edit_category'),
    path('settings/categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('settings/items/add/', views.add_menu_item, name='add_menu_item'),
    path('settings/items/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('settings/items/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),

    path('table/add/', views.add_table, name='add_table'),
    path('table/edit/', views.edit_table, name='edit_table'),
    path('table/delete/<int:table_id>/', views.delete_table, name='delete_table'),
]