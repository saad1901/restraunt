from django.urls import path
from .policy_views import *
from .views import *

urlpatterns = [
    path('', homepage, name='frontsite'),      
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    path('cookies/', cookies_view, name='cookies'),
    path('help-center/', help_center_view, name='help-center'),
    path('documentation/', documentation_view, name='documentation'),
    path('api/', api_view, name='api'),
    path('status/', status_view, name='status')
]