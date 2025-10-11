from authn.setupView import owner_register, hotel_register
from django.contrib.staticfiles.views import serve
from userApp import views as userview
from django.contrib import admin
from django.urls import path, include
from app import views
from authn.views import owner_login

urlpatterns = [
    path('', owner_login),
    path('owner/', include('owner.urls')),
    path('staff/', include('staff.urls')),
    path('superadmin/', include('superadmin.urls')),
    path('agent/', include('agent.urls')),
    path('site/', include('frontsite.urls')),
    path('auth/', include('authn.urls')),
    path('demo/', include('demo.urls')),

    path('register/owner/', owner_register, name='owner_register'),
    path('register/hotel/', hotel_register, name='hotel_register'),

    path('admin/', admin.site.urls),

    path('user/getmenu/<int:hotel>/', userview.show_menu, name='user_show_menu'),
    path('user/getmenu/<int:hotel>/<int:table>/', userview.show_menu, name='user_show_menu'),

    path('serviceworker.js', serve, kwargs={'path': 'js/serviceworker.js'}),

]