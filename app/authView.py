from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def owner_login(request):
    if request.user.is_authenticated:
        return redirect('redirection')
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
            elif user.role == 'agent':
                return redirect('agenthome')
            elif user.role == 'superadmin':
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('owner_login')