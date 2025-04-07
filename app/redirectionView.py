from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from app.models import Hotel

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