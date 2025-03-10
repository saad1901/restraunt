from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def owner_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'owner':
                return redirect('owner')
            elif user.role == 'staff':
                return redirect('waiterhome')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')
