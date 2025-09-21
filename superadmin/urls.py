from django.urls import path
from .views import *

urlpatterns = [
    path('home/', home, name='home'),
    path('git_pull', git_pull, name='git_pull'),
    path('system/operations/', system_operations, name='system_operations'),
    
    # Database Management URLs
    path('system/database/', database_management, name='database_management'),
    path('system/database/backup/', create_backup, name='create_backup'),
    path('system/database/restore/<str:backup_id>/', restore_backup, name='restore_backup'),
    path('system/database/delete/<str:backup_id>/', delete_backup, name='delete_backup'),
    path('system/database/optimize/', optimize_database, name='optimize_database'),
    
    path('addagent/', addagent, name='addagent'),
    
    # Admin Analytics Dashboard routes
    path('admin/analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('admin/financial-reports/', financial_reports, name='financial_reports'),
    path('admin/user-activity/', user_activity, name='user_activity'),
    
    path('home/users', users, name='users'),
    path('home/users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('home/users/view/<int:user_id>/', view_user, name='view_user'),
    path('home/users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('home/users/toggle-status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('home/restaurant/view/<int:hotel_id>/', view_restaurant, name='view_restaurant'),
    path('home/toggle/<int:hotel_id>', toggle_hotel_status, name='toggle_hotel_status'),
    
]