from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User, Hotel
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    hotels = Hotel.objects.all()
    return render(request, 'Admin/home.html', {'hotels': hotels})
