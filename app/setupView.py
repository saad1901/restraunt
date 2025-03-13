from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import OwnerRegistrationForm, HotelRegistrationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
User = get_user_model()


def owner_register(request):
    # if request.user.role not in ['superadmin', 'agent']:
    #     return redirect('owner_login')
    
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
    # if request.user.role not in ['superadmin', 'agent']:
    #     return redirect('owner_login')
    # Ensure we have the owner_id stored in the session
    owner_id = request.session.get('owner_id')
    if not owner_id:
        return redirect('owner_register')
    
    if request.method == 'POST':
        form = HotelRegistrationForm(request.POST)
        if form.is_valid():
            hotel = form.save(commit=False)
            # Link the hotel to the newly registered owner.
            owner = get_object_or_404(User, id=owner_id)
            hotel.owner = owner
            hotel.save()
            user = User.objects.get(id=owner_id)  # Replace user_id with actual user ID
            user.staffof = hotel
            user.save()
            # Clear the session key after use.
            del request.session['owner_id']
            # Redirect to login page or a success page.

            print(1)

            if not request.user.is_authenticated:
                print(2.2)
                print(owner.username)
                print(owner.password)
                user = authenticate(request, username=owner.username, password=owner.hint)
                if user is not None:
                    login(request, user)
                    return redirect('owner')
                else:
                    print(2.3)
                    messages.error(request, "Authentication failed. Please check your credentials.")
                    return redirect('owner_register')
            print(3)
            if request.user.role == 'superadmin':
                return redirect('home')
            elif request.user.role == 'agent':
                return redirect('agenthome')
            else:
                user = authenticate(request, username=owner.username, password=owner.hint)
                login(request, user)
                return redirect('owner')
            
    form = HotelRegistrationForm()
    return render(request, 'registration/hotel_register.html', {'form': form})


def register(request):
    return render(request, 'RegisterUser/register.html')