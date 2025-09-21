from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import Hotel

def owner_login(request):
    if request.user.is_authenticated:
        return redirect('redirection')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect all users to redirection view which will handle proper routing
            return redirect('redirection')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html')

def logout_user(request):
    logout(request)
    return redirect('owner_login')

@login_required
def redirection(request):
    user = request.user
    if user.role == 'superadmin':
        return redirect('home')
    elif user.role == 'owner':
        # Check if the owner has registered a restaurant
        hotel_exists = Hotel.objects.filter(owner=user).exists()
        if not hotel_exists:
            # If no restaurant is registered, redirect to restaurant registration page
            return redirect('hotel_register')
        return redirect('owner')
    elif user.role == 'staff':
        return redirect('waiterhome')
    elif user.role == 'agent':
        print('x')
        return redirect('agenthome')
    else:
        return redirect('owner_login')