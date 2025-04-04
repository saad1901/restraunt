from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import User, Hotel, Table, MenuCategory, MenuItem, Order, OrderItems
from django.contrib.auth.decorators import login_required
from app.forms import AgentRegisterForm
from app.sendmail import sendemail
import subprocess
from django.http import JsonResponse
from django.db.models import Count, Sum
import os
import sys
import django
import platform

@login_required
def home(request):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    hotels = Hotel.objects.all()
    
    # Add counts for different roles
    owners_count = User.objects.filter(role='owner').count()
    agents_count = User.objects.filter(role='agent').count()
    
    # Calculate active hotels count directly in the view
    active_hotels_count = hotels.filter(status=True).count()
    
    if request.method == 'POST' and 'q' in request.POST:
        query = request.POST.get('q', '').strip()
        if query:
            hotels = hotels.filter(name__icontains=query)

    context = {
        'hotels': hotels,
        'owners_count': owners_count,
        'agents_count': agents_count,
        'active_hotels_count': active_hotels_count,
    }
    return render(request, 'Admin/home.html', context)

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
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    users = User.objects.all()
    
    # Add counts for the stats cards
    active_users = users.filter(is_active=True).count()
    agent_count = users.filter(role='agent').count()
    superadmin_count = users.filter(role='superadmin').count()
    
    # Add related hotels
    hotels = Hotel.objects.all()
    
    context = {
        'users': users,
        'active_users': active_users,
        'agent_count': agent_count,
        'superadmin_count': superadmin_count,
        'hotels': hotels,
    }
    
    return render(request, 'Admin/users.html', context)


@login_required
def delete_user(request, user_id):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Don't allow deleting superadmin
        if user_to_delete.role == 'superadmin':
            messages.error(request, 'Cannot delete admin user.')
            return redirect('users')
        
        # Store username for the success message
        username = user_to_delete.username
        
        # Delete the user
        user_to_delete.delete()
        
        messages.success(request, f'User "{username}" has been successfully deleted.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('users')


@login_required
def system_operations(request):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    # To store the results of operations
    results = {
        'has_result': False,
        'operation': None,
        'status': None,
        'output': None,
        'error': None
    }
    
    # Get the current project path
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Get system information
    user_count = User.objects.count()
    hotel_count = Hotel.objects.count()
    active_hotel_count = Hotel.objects.filter(status=True).count()
    
    # Get the last deployment time (simple placeholder approach)
    try:
        from datetime import datetime
        git_dir = os.path.join(project_path, '.git')
        if os.path.exists(git_dir):
            head_file = os.path.join(git_dir, 'FETCH_HEAD')
            if os.path.exists(head_file):
                last_deployment = datetime.fromtimestamp(os.path.getmtime(head_file)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_deployment = "Unknown"
        else:
            last_deployment = "Git not initialized"
    except:
        last_deployment = "Could not determine"
    
    if request.method == 'POST':
        operation = request.POST.get('operation')
        results['operation'] = operation
        results['has_result'] = True
        
        try:
            if operation == 'git_pull':
                # Run git pull command
                result = subprocess.run(
                    ["git", "pull"],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                results['status'] = "success" if result.returncode == 0 else "error"
                results['output'] = result.stdout
                results['error'] = result.stderr
                
            elif operation == 'migrations':
                # Run makemigrations command
                result = subprocess.run(
                    ["python", "manage.py", "makemigrations"],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                results['status'] = "success" if result.returncode == 0 else "error"
                results['output'] = result.stdout
                results['error'] = result.stderr
                
            elif operation == 'migrate':
                # Run migrate command
                result = subprocess.run(
                    ["python", "manage.py", "migrate"],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                results['status'] = "success" if result.returncode == 0 else "error"
                results['output'] = result.stdout
                results['error'] = result.stderr
                
            elif operation == 'collectstatic':
                # Run collectstatic command
                result = subprocess.run(
                    ["python", "manage.py", "collectstatic", "--noinput"],
                    cwd=project_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                results['status'] = "success" if result.returncode == 0 else "error"
                results['output'] = result.stdout
                results['error'] = result.stderr
                
            elif operation == 'restart_server':
                # This is a placeholder - actual server restart depends on your deployment
                results['status'] = "info"
                results['output'] = "Server restart command would be executed here in production."
                results['error'] = "Note: In development, you'll need to restart the server manually."
        
        except Exception as e:
            results['status'] = "error"
            results['error'] = str(e)
    
    # Create system information for context
    system_info = {
        'python_version': platform.python_version(),
        'django_version': django.get_version(),
        'os': platform.platform(),
    }
    
    context = {
        'results': results,
        'user_count': user_count,
        'hotel_count': hotel_count,
        'active_hotel_count': active_hotel_count,
        'last_deployment': last_deployment,
        'system_info': system_info
    }
    
    return render(request, 'Admin/system_operations.html', context)


@login_required
def git_pull(request):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    # Redirect to the system operations page
    return redirect('system_operations')


@login_required
def view_user(request, user_id):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    try:
        user = User.objects.get(id=user_id)
        hotels = Hotel.objects.all()
        
        # Count hotels for agent
        agent_hotels = []
        if user.role == 'agent':
            agent_hotels = hotels.filter(agent=user)
        
        # Find hotel for owner
        owner_hotel = None
        if user.role == 'owner':
            owner_hotel = hotels.filter(owner=user).first()
        
        context = {
            'user_detail': user,
            'agent_hotels': agent_hotels,
            'owner_hotel': owner_hotel
        }
        
        return render(request, 'Admin/view_user.html', context)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('users')


@login_required
def edit_user(request, user_id):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    try:
        user = User.objects.get(id=user_id)
        
        if request.method == 'POST':
            # Handle superadmin protection
            if user.role == 'superadmin' and user.role != request.POST.get('role', 'superadmin'):
                messages.error(request, 'Cannot change role of admin user.')
                return redirect('users')
            
            # Update user fields
            user.username = request.POST.get('username', user.username)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', user.phone)
            user.city = request.POST.get('city', user.city)
            user.is_active = request.POST.get('is_active') == 'on'
            
            # Only change role if user is not superadmin
            if user.role != 'superadmin':
                user.role = request.POST.get('role', user.role)
                
            # Change password if provided
            password = request.POST.get('password')
            if password and len(password) >= 6:
                user.set_password(password)
            
            user.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('users')
            
        return render(request, 'Admin/edit_user.html', {'user_detail': user})
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('users')


@login_required
def toggle_user_status(request, user_id):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    try:
        user = User.objects.get(id=user_id)
        
        # Don't allow deactivating superadmin
        if user.role == 'superadmin':
            messages.error(request, 'Cannot change status of admin user.')
            return redirect('users')
        
        # Toggle status
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User '{user.username}' {status} successfully.")
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('users')


@login_required
def view_restaurant(request, hotel_id):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    try:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        
        # Get tables
        tables = Table.objects.filter(hotel=hotel)
        
        # Get menu categories and items
        menu_categories = MenuCategory.objects.filter(hotel=hotel)
        menu_items = MenuItem.objects.filter(hotel=hotel)
        
        # Get staff members
        staff = User.objects.filter(staffof=hotel)
        
        # Get recent orders
        recent_orders = Order.objects.filter(hotel=hotel).order_by('-created_at')[:10]
        
        # Calculate statistics
        total_tables = tables.count()
        total_menu_items = menu_items.count()
        total_categories = menu_categories.count()
        total_orders = Order.objects.filter(hotel=hotel).count()
        completed_orders = Order.objects.filter(hotel=hotel, completed=True).count()
        
        # Calculate completion rate
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        context = {
            'hotel': hotel,
            'tables': tables,
            'menu_categories': menu_categories,
            'menu_items': menu_items,
            'staff': staff,
            'recent_orders': recent_orders,
            'total_tables': total_tables,
            'total_menu_items': total_menu_items,
            'total_categories': total_categories,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'completion_rate': completion_rate,
        }
        
        return render(request, 'Admin/view_restaurant.html', context)
    except Hotel.DoesNotExist:
        messages.error(request, 'Restaurant not found.')
        return redirect('home')
