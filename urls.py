from django.urls import path
from . import views

urlpatterns = [
    # ... existing URLs ...
    
    # Database Management URLs
    path('database/', views.database_management, name='database_management'),
    path('database/backup/', views.create_backup, name='create_backup'),
    path('database/restore/<str:backup_id>/', views.restore_backup, name='restore_backup'),
    path('database/delete/<str:backup_id>/', views.delete_backup, name='delete_backup'),
    path('database/optimize/', views.optimize_database, name='optimize_database'),
    
    # ... existing URLs ...
] 