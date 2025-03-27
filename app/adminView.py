from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User, Hotel
from django.contrib.auth.decorators import login_required
from app.forms import AgentRegisterForm
from app.sendmail import sendemail
import subprocess
from django.http import JsonResponse

@login_required
def home(request):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    hotels = Hotel.objects.all()
    if request.method == 'POST' and 'q' in request.POST:
        query = request.POST.get('q', '').strip()
        if query:
            hotels = hotels.filter(name__icontains=query)

    return render(request, 'Admin/home.html', {'hotels': hotels})

def addagent(request):
    form = AgentRegisterForm()
    if request.method == 'POST':
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            sendemail(form.cleaned_data.get('email'), 'Agent Registration', 'You have been registered as an agent.')
            messages.success(request, 'Agent added successfully.')
            return redirect('home')
    return render(request, 'Admin/addagent.html', {'form': form})


def users(request):
    users = User.objects.all()
    return render(request, 'Admin/users.html', {'users': users})



# from django.contrib.admin.views.decorators import staff_member_required
@login_required  # Restrict access to admin users
def git_pull(request):
    if request.user.role != 'superadmin':
        return JsonResponse('F**k off')
    try:
        project_path = "/home/hotelsoftware/restraunt"  # Your project directory
        
        # Run git pull command
        result = subprocess.run(
            ["git", "pull"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return JsonResponse({
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr
        })

    except Exception as e:
        return JsonResponse({"status": "error", "error": str(e)})
