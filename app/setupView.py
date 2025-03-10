from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import OwnerRegistrationForm, HotelRegistrationForm
from django.contrib.auth import get_user_model

User = get_user_model()

def owner_register(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            owner = form.save()
            hint = form.cleaned_data.get('password2')
            owner.hint = hint
            # Save the owner's id in the session for the next step.
            request.session['owner_id'] = owner.id
            return redirect('hotel_register')
    else:
        form = OwnerRegistrationForm()
    return render(request, 'registration/owner_register.html', {'form': form})

def hotel_register(request):
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
            return redirect('owner')
    else:
        form = HotelRegistrationForm()
    return render(request, 'registration/hotel_register.html', {'form': form})
