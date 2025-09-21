from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from app.forms import OwnerRegistrationForm, HotelRegistrationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from app.models import Hotel
User = get_user_model()

def owner_register(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            owner = form.save()
            request.session['owner_id'] = owner.id
            return redirect('hotel_register')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/owner_register.html', {'form': form})


def hotel_register(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        # If the user is not an owner, agent, or superadmin, they cannot register a restaurant
        if request.user.role not in ['owner', 'agent', 'superadmin']:
            messages.error(request, "You are not authorized to register a restaurant.")
            return redirect('owner_login')
            
        # If user is an owner
        if request.user.role == 'owner':
            # Check if this owner already has a hotel
            if Hotel.objects.filter(owner=request.user).exists():
                return redirect('owner')
            # Set owner_id for hotel creation
            owner_id = request.user.id
        elif request.user.role in ['agent', 'superadmin']:
            # For agent or superadmin, check if we have an owner_id in session
            owner_id = request.session.get('owner_id')
            if not owner_id:
                return redirect('owner_register')
    else:
        # Handle normal registration flow for unauthenticated users
        owner_id = request.session.get('owner_id')
        if not owner_id:
            return redirect('owner_register')
    
    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            
            # Link the hotel to the owner
            owner = get_object_or_404(User, id=owner_id)
            hotel.owner = owner
            
            # Assign agent based on who's creating the restaurant
            if request.user.is_authenticated:
                if request.user.role == 'agent':
                    # If the creator is an agent, set them as the agent
                    hotel.agent = request.user
                elif request.user.role == 'superadmin':
                    # If superadmin is creating, no agent is assigned
                    hotel.agent = None
            
            hotel.save()
            
            # Update user's staffof field
            owner.staffof = hotel
            owner.save()
            
            # Clear session data if it exists
            if 'owner_id' in request.session:
                del request.session['owner_id']

            if not request.user.is_authenticated:
                user = authenticate(request, username=owner.username, password=owner.hint)
                if user is not None:
                    login(request, user)
                    return redirect('owner')
                else:
                    messages.error(request, "Authentication failed. Please check your credentials.")
                    return redirect('owner_register')
            
            if request.user.role == 'superadmin':
                messages.success(request, f"Restaurant '{hotel.name}' registered successfully.")
                return redirect('home')
            elif request.user.role == 'agent':
                messages.success(request, f"Restaurant '{hotel.name}' registered successfully and assigned to you.")
                return redirect('agenthome')
            else:
                messages.success(request, f"Your restaurant '{hotel.name}' has been registered successfully.")
                return redirect('owner')
            
    form = HotelRegistrationForm()
    return render(request, 'registration/hotel_register.html', {'form': form})


def register(request):
    return render(request, 'RegisterUser/register.html')