from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirection(request):
    user = request.user
    if user.role == 'superadmin':
        return redirect('home')
    elif user.role == 'owner':
        return redirect('owner')
    elif user.role == 'staff':
        return redirect('waiterhome')
    elif user.role == 'agent':
        print('x')
        return redirect('agenthome')
    else:
        return redirect('owner_login')