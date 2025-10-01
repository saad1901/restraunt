from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('git_pull', git_pull, name='git_pull'),
    path('system/', system_operations, name='system_operations'),
    path('system/database/', database_management, name='database_management'),
    path('system/database/backup/', create_backup, name='create_backup'),
    path('system/database/restore/<str:backup_id>/', restore_backup, name='restore_backup'),
    path('system/database/delete/<str:backup_id>/', delete_backup, name='delete_backup'),
    path('system/database/optimize/', optimize_database, name='optimize_database'),
    path('addagent/', addagent, name='addagent'),
    path('analytics/', analytics_dashboard, name='analytics_dashboard'),
    path('financial-reports/', financial_reports, name='financial_reports'),
    path('user-activity/', user_activity, name='user_activity'),
    path('logs/', logs, name='logs'),
    path('users/', users, name='users'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/view/<int:user_id>/', view_user, name='view_user'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/toggle-status/<int:user_id>/', toggle_user_status, name='toggle_user_status'),
    path('restaurant/view/<int:hotel_id>/', view_restaurant, name='view_restaurant'),
    path('toggle/<int:hotel_id>/', toggle_hotel_status, name='toggle_hotel_status'),
    path('adminplans/', adminplans, name='adminplans'),
    path('deleteplan/<int:plan_id>/', delete_plan, name='delete_plan')  
]