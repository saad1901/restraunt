from django.contrib import admin
from django.urls import path
from app import views
from app.setupView import owner_register, hotel_register, register
from app.authView import owner_login, logout_user
from app.adminView import home, addagent, users, git_pull, delete_user, view_user, edit_user, toggle_user_status, view_restaurant, system_operations, database_management, create_backup, restore_backup, delete_backup, optimize_database
from app.redirectionView import redirection
from app.agentView import agenthome
from app.policy_views import terms_view, privacy_view, cookies_view, help_center_view, documentation_view, api_view, status_view
from django.views.generic import TemplateView
from django.contrib.staticfiles.views import serve

# USERAPP IMPORTS
from userApp import views as userview

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('home/', home, name='home'),
    path('git_pull', git_pull, name='git_pull'),
    path('system/operations/', system_operations, name='system_operations'),
    
    # Database Management URLs
    path('system/database/', database_management, name='database_management'),
    path('system/database/backup/', create_backup, name='create_backup'),
    path('system/database/restore/<str:backup_id>/', restore_backup, name='restore_backup'),
    path('system/database/delete/<str:backup_id>/', delete_backup, name='delete_backup'),
    path('system/database/optimize/', optimize_database, name='optimize_database'),
    
    # Policy and Documentation Pages
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    path('cookies/', cookies_view, name='cookies'),
    path('help-center/', help_center_view, name='help-center'),
    path('documentation/', documentation_view, name='documentation'),
    path('api/', api_view, name='api'),
    path('status/', status_view, name='status'),
    
    # Admin Analytics Dashboard routes
    path('admin/analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('admin/financial-reports/', views.financial_reports, name='financial_reports'),
    path('admin/user-activity/', views.user_activity, name='user_activity'),
    
    path('home/users', users, name='users'),
    path('home/users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('home/users/view/<int:user_id>/', view_user, name='view_user'),
    path('home/users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('home/users/toggle-status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('home/restaurant/view/<int:hotel_id>/', view_restaurant, name='view_restaurant'),
    path('home/toggle/<int:hotel_id>', views.toggle_hotel_status, name='toggle_hotel_status'),
    
    path('booking/', views.home, name='waiterhome'),
    path('payment/', views.payment, name='payment'),

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
    path('owner/staff/deletestaff', views.delete_staff, name='delete_staff'),

    path('submit-order/', views.submit_order, name='submit_order'),
    path('complete_order/', views.complete_order, name='complete_order'),
    path('delete_order/', views.delete_order, name='delete_order'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('ajax/get_orders/', views.ajax_get_orders, name='ajax_get_orders'),

    path('owner/settings', views.button, name='button'),
    path('owner/settings/reports', views.reports, name='reports'),

    path('owner/settings/reports/sales', views.sales, name='sales'),
    path('owner/settings/reports/sales/dailytransc', views.dailytransc, name='dailytransc'),
    path('owner/settings/reports/sales/monthlytransac', views.monthly_report, name='monthlytransac'),
    path('owner/settings/reports/sales/custom_period', views.custom_period, name='custom_period'),
    
    path('owner/settings/reports/revenue', views.revenue, name='revenue'),
    path('owner/settings/reports/inventory', views.inventory, name='inventory'),
    path('owner/settings/reports/inventory/add', views.add_inventory_item, name='add_inventory_item'),
    path('owner/settings/reports/inventory/edit', views.edit_inventory_item, name='edit_inventory_item'),
    path('owner/settings/reports/inventory/delete/<int:item_id>/', views.delete_inventory_item, name='delete_inventory_item'),
    path('owner/settings/reports/inventory/transaction', views.inventory_transaction, name='inventory_transaction'),
    path('owner/settings/reports/inventory/history', views.inventory_history, name='inventory_history'),
    
    path('owner/settings/reports/timeanalysis', views.timeanalysis, name='timeanalysis'),

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

    path('user/getmenu/<int:hotel>/<int:table>', userview.show_menu, name='user_show_menu'),

    path('serviceworker.js', serve, 
         kwargs={'path': 'js/serviceworker.js'}),
]