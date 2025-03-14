from django.contrib import admin
from django.urls import path
from app import views
from app.setupView import owner_register, hotel_register, register
from app.authView import owner_login, logout_user
from app.adminView import home, addagent, users
from app.redirectionView import redirection
from app.agentView import agenthome
urlpatterns = [
    path('home/', home, name='home'),
    path('home/users', users, name='users'),
    path('booking/', views.home, name='waiterhome'),
    path('home/toggle/<int:hotel_id>', views.toggle_hotel_status, name='toggle_hotel_status'),

    path('login/', owner_login, name='owner_login'),
    path('logout/', logout_user, name='logout'),

    path('register/', register, name='register'),
    path('addagent/', addagent, name='addagent'),

    path('agent/', agenthome, name='agenthome'),

    path('register/owner/', owner_register, name='owner_register'),
    path('register/hotel/', hotel_register, name='hotel_register'),

    path('admin/', admin.site.urls),
    path('', redirection, name='redirection'),
    path('owner/', views.owner, name='owner'),
    path('owner/staff/', views.staff, name='staff'),
    path('owner/staff/addstaff', views.add_staff, name='add_staff'),
    path('owner/staff/editstaff', views.edit_staff, name='edit_staff'),

    path('submit-order/', views.submit_order, name='submit_order'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),

    path('settings', views.button, name='button'),
    path('reports', views.reports, name='reports'),

    path('settings/categories/', views.category, name='category'),
    path('settings/categories/add/', views.add_category, name='add_category'),
    path('settings/categories/edit/', views.edit_category, name='edit_category'),
    path('settings/categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    
    path('settings/items/', views.item, name='item'),
    path('settings/items/add/', views.add_menu_item, name='add_menu_item'),
    path('settings/items/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('settings/items/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),

    path('settings/table/', views.table, name='table'),
    path('settings/table/add/', views.add_table, name='add_table'),
    path('settings/table/edit/', views.edit_table, name='edit_table'),
    path('settings/table/delete/<int:table_id>/', views.delete_table, name='delete_table'),

]