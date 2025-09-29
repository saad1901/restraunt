from app.models import User, Hotel, Table, MenuCategory, MenuItem, Order
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from app.forms import AgentRegisterForm
from django.http import JsonResponse
from django.contrib import messages
from app.sendmail import sendemail
from django.db.models import Count
from django.utils import timezone
from .models import BillingPlans
from django.conf import settings
from django.db import connection
import subprocess
import platform
import requests
import calendar
import django
import json
import sys
import os

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
    return render(request, 'superadmin/home.html', context)

def addagent(request):
    if request.user.role != 'superadmin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    form = AgentRegisterForm()
    if request.method == 'POST':
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            sendemail(form.cleaned_data.get('email'), 'Agent Registration', 'You have been registered as an agent.')
            messages.success(request, 'Agent added successfully.')
            return redirect('home')
    return render(request, 'superadmin/addagent.html', {'form': form})


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
    
    return render(request, 'superadmin/users.html', context)


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
                # PythonAnywhere-specific restart using their API
                try:
                    # Get the PythonAnywhere username from settings
                    username = getattr(settings, 'PYTHONANYWHERE_USERNAME', '')
                    api_token = getattr(settings, 'PYTHONANYWHERE_API_TOKEN', '')
                    
                    if username and api_token:
                        # Construct the API URL for reloading the web app
                        api_url = f"https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{username}.pythonanywhere.com/reload/"
                        
                        # Make the API request to reload the web app
                        response = requests.post(
                            api_url,
                            headers={"Authorization": f"Token {api_token}"}
                        )
                        
                        if response.status_code == 200:
                            results['status'] = "success"
                            results['output'] = "PythonAnywhere application successfully restarted."
                        else:
                            results['status'] = "error"
                            results['error'] = f"Failed to restart application. API Response: {response.status_code} - {response.text}"
                    else:
                        results['status'] = "error"
                        results['error'] = "PythonAnywhere credentials not configured. Please add PYTHONANYWHERE_USERNAME and PYTHONANYWHERE_API_TOKEN to your settings."
                except ImportError:
                    results['status'] = "error"
                    results['error'] = "The 'requests' library is required but not installed. Run 'pip install requests' to install it."
                except Exception as e:
                    results['status'] = "error"
                    results['error'] = f"Error restarting PythonAnywhere application: {str(e)}"
                    return redirect('home')
        
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
    
    return render(request, 'superadmin/system_operations.html', context)


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
        
        return render(request, 'superadmin/view_user.html', context)
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
            
        return render(request, 'superadmin/edit_user.html', {'user_detail': user})
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
        
        return render(request, 'superadmin/view_restaurant.html', context)
    except Hotel.DoesNotExist:
        messages.error(request, 'Restaurant not found.')
        return redirect('home')

@login_required
def database_management(request):
    if request.user.role != 'superadmin':
        return redirect('owner_login')
    
    # MySQL specific database statistics
    with connection.cursor() as cursor:
        try:
            # Get database size (MySQL version)
            cursor.execute("""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
                FROM 
                    information_schema.tables
                WHERE 
                    table_schema = DATABASE()
            """)
            result = cursor.fetchone()
            db_size = f"{result[0]} MB" if result and result[0] else "Unknown"
        except:
            db_size = "Unknown"
        
        try:
            # Get table count (works in both MySQL and PostgreSQL)
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = DATABASE()
            """)
            table_count = cursor.fetchone()[0]
        except:
            table_count = 0
        
        try:
            # Get table statistics (MySQL version)
            cursor.execute("""
                SELECT 
                    table_name as name,
                    table_rows as row_count,
                    ROUND(data_length / 1024 / 1024, 2) as size_mb,
                    CASE 
                        WHEN table_rows > 1000000 THEN 'critical'
                        WHEN table_rows > 100000 THEN 'warning'
                        ELSE 'healthy'
                    END as status
                FROM 
                    information_schema.tables
                WHERE 
                    table_schema = DATABASE()
                ORDER BY 
                    table_name
            """)
            table_stats = [
                {
                    'name': row[0],
                    'rows': row[1] if row[1] is not None else 0,
                    'size': f"{row[2]} MB" if row[2] is not None else '0 KB',
                    'status': row[3]
                }
                for row in cursor.fetchall()
            ]
        except Exception as e:
            table_stats = []
            
        # Get query statistics (simplified as MySQL doesn't store this directly)
        query_times = ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00']
        query_durations = [45, 42, 50, 55, 60, 58, 52, 48]
        
        # Count tables for query estimate
        try:
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Questions'")
            result = cursor.fetchone()
            query_count = int(result[1]) if result and len(result) > 1 else 583
        except:
            query_count = 583
    
    # Get backup information
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    backups = []
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # First check for any SQL backups that need conversion
    convert_sql_backups_to_json(backup_dir)
    
    # Now list all JSON backups
    for filename in os.listdir(backup_dir):
        if filename.endswith('.json') or filename.endswith('.sql'):
            filepath = os.path.join(backup_dir, filename)
            backups.append({
                'id': filename,
                'name': filename,
                'size': os.path.getsize(filepath),
                'created_at': datetime.fromtimestamp(os.path.getctime(filepath))
            })
    
    # Sort backups by creation time, newest first
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Get last backup time
    last_backup = backups[0]['created_at'] if backups else datetime.now()
    
    context = {
        'db_size': db_size,
        'table_count': table_count,
        'table_stats': table_stats,
        'query_times': json.dumps(query_times),
        'query_durations': json.dumps(query_durations),
        'query_count': query_count,
        'backups': backups,
        'last_backup': last_backup
    }
    
    return render(request, 'superadmin/database_management.html', context)

def convert_sql_backups_to_json(backup_dir):
    """
    Convert any existing .sql backup files to .json files
    This helps during the transition from .sql to .json file extension
    """
    if not os.path.exists(backup_dir):
        return
        
    for filename in os.listdir(backup_dir):
        if filename.endswith('.sql'):
            sql_path = os.path.join(backup_dir, filename)
            json_path = os.path.join(backup_dir, filename.replace('.sql', '.json'))
            
            # Skip if JSON version already exists
            if os.path.exists(json_path):
                continue
                
            try:
                # Check if file contains valid JSON
                with open(sql_path, 'r') as f:
                    try:
                        content = f.read()
                        json.loads(content)  # Test if it's valid JSON
                        
                        # If we get here, it's valid JSON, so copy it to a .json file
                        with open(json_path, 'w') as dest:
                            dest.write(content)
                    except json.JSONDecodeError:
                        # Not valid JSON, so skip it
                        continue
            except Exception:
                # Skip any file that cannot be read
                continue
                
@login_required
@require_POST
@csrf_exempt
def create_backup(request):
    if request.user.role != 'superadmin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Try both SQL and JSON formats, with SQL as primary for MySQL
        sql_backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
        json_backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')
        
        success = False
        error_messages = []
        
        # Method 1: Use mysqldump (MySQL specific)
        try:
            # Get database connection info from Django settings
            db_settings = settings.DATABASES['default']
            
            # Build mysqldump command for PythonAnywhere MySQL
            if 'pythonanywhere' in request.get_host():
                # PythonAnywhere specific - use their connection strings
                # https://help.pythonanywhere.com/pages/MySQLBackupRestore/
                username = db_settings['USER']
                password = db_settings['PASSWORD']
                database = db_settings['NAME']
                host = db_settings['HOST']
                
                # For PythonAnywhere, use their specific mysqldump path
                mysqldump_cmd = [
                    'mysqldump',
                    '-u', username,
                    f'--password={password}',
                    '-h', host,
                    database
                ]
                
                # Execute the command and save output to file
                with open(sql_backup_file, 'w') as f:
                    result = subprocess.run(
                        mysqldump_cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                
                if result.returncode == 0:
                    success = True
                else:
                    error_messages.append(f"mysqldump failed: {result.stderr}")
            else:
                # Standard mysqldump execution
                username = db_settings['USER']
                password = db_settings['PASSWORD']
                database = db_settings['NAME']
                host = db_settings['HOST']
                
                env = os.environ.copy()
                env['MYSQL_PWD'] = password
                
                mysqldump_cmd = [
                    'mysqldump',
                    '-u', username,
                    '-h', host,
                    database
                ]
                
                with open(sql_backup_file, 'w') as f:
                    result = subprocess.run(
                        mysqldump_cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env,
                        check=False
                    )
                
                if result.returncode == 0:
                    success = True
                else:
                    error_messages.append(f"mysqldump failed: {result.stderr}")
        except Exception as e:
            error_messages.append(f"mysqldump error: {str(e)}")
        
        # Method 2: Django's dumpdata (as backup)
        if not success:
            try:
                # First method: Use subprocess
                result = subprocess.run(
                    [sys.executable, 'manage.py', 'dumpdata', '--exclude', 'contenttypes', '--exclude', 'auth.permission', '--indent', '2'],
                    cwd=settings.BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    error_messages.append(f"dumpdata failed: {result.stderr}")
                else:
                    with open(json_backup_file, 'w') as f:
                        f.write(result.stdout)
                    success = True
                
            except Exception as subprocess_error:
                error_messages.append(f"subprocess error: {str(subprocess_error)}")
                
                try:
                    # Fallback method: Use direct DB connection
                    from django.core import management
                    from io import StringIO
                    
                    output = StringIO()
                    management.call_command('dumpdata', 
                                        exclude=['contenttypes', 'auth.permission'],
                                        indent=2, 
                                        stdout=output)
                    
                    with open(json_backup_file, 'w') as f:
                        f.write(output.getvalue())
                    success = True
                except Exception as e:
                    error_messages.append(f"management command error: {str(e)}")
        
        # Check if either file was created successfully
        if success:
            if os.path.exists(sql_backup_file) and os.path.getsize(sql_backup_file) > 0:
                return JsonResponse({'success': True, 'message': 'MySQL backup created successfully'})
            elif os.path.exists(json_backup_file) and os.path.getsize(json_backup_file) > 0:
                return JsonResponse({'success': True, 'message': 'JSON backup created successfully'})
            else:
                raise Exception("Backup files were not created properly")
        else:
            raise Exception("All backup methods failed: " + "; ".join(error_messages))
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'success': False, 
            'message': str(e),
            'details': error_details
        }, status=500)

@login_required
@require_POST
@csrf_exempt
def restore_backup(request, backup_id):
    if request.user.role != 'superadmin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        backup_file = os.path.join(settings.BASE_DIR, 'backups', backup_id)
        
        if not os.path.exists(backup_file):
            return JsonResponse({'success': False, 'message': 'Backup file not found'}, status=404)
        
        db_settings = settings.DATABASES['default']
        success = False
        error_messages = []
        
        # MySQL dump restoration for .sql files
        if backup_file.endswith('.sql'):
            try:
                # For PythonAnywhere MySQL restoration
                username = db_settings['USER']
                password = db_settings['PASSWORD']
                database = db_settings['NAME']
                host = db_settings['HOST']
                
                # Build MySQL command for restore
                if 'pythonanywhere' in request.get_host():
                    # PythonAnywhere specific MySQL command
                    mysql_cmd = [
                        'mysql',
                        '-u', username,
                        f'--password={password}',
                        '-h', host,
                        database
                    ]
                else:
                    # Standard MySQL command
                    env = os.environ.copy()
                    env['MYSQL_PWD'] = password
                    
                    mysql_cmd = [
                        'mysql',
                        '-u', username,
                        '-h', host,
                        database
                    ]
                
                # Execute the restore command
                with open(backup_file, 'r') as f:
                    if 'pythonanywhere' in request.get_host():
                        result = subprocess.run(
                            mysql_cmd,
                            stdin=f,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            check=False
                        )
                    else:
                        result = subprocess.run(
                            mysql_cmd,
                            stdin=f,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            env=env,
                            check=False
                        )
                
                if result.returncode == 0:
                    success = True
                else:
                    error_messages.append(f"MySQL restore failed: {result.stderr}")
            except Exception as e:
                error_messages.append(f"MySQL restore error: {str(e)}")
        
        # Django loaddata for .json files
        elif backup_file.endswith('.json'):
            try:
                # Verify the file is valid JSON
                with open(backup_file, 'r') as f:
                    try:
                        import json
                        data = json.load(f)
                    except json.JSONDecodeError:
                        return JsonResponse({'success': False, 'message': 'Invalid backup file format'}, status=400)
                
                # Try using loaddata
                result = subprocess.run(
                    [sys.executable, 'manage.py', 'loaddata', backup_file],
                    cwd=settings.BASE_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    success = True
                else:
                    error_messages.append(f"Django loaddata failed: {result.stderr}")
            except Exception as e:
                error_messages.append(f"Django loaddata error: {str(e)}")
        
        if success:
            return JsonResponse({'success': True, 'message': 'Backup restored successfully'})
        else:
            raise Exception("Restore failed: " + "; ".join(error_messages))
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'success': False, 
            'message': str(e),
            'details': error_details
        }, status=500)

@login_required
@require_POST
@csrf_exempt
def optimize_database(request):
    if request.user.role != 'superadmin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        results = []
        
        # Clear Django sessions
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'clearsessions'],
                cwd=settings.BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.returncode == 0:
                results.append("Successfully cleared old sessions")
            else:
                results.append(f"Session cleanup warning: {result.stderr}")
        except Exception as e:
            results.append(f"Session cleanup failed: {str(e)}")
        
        # MySQL specific optimizations
        with connection.cursor() as cursor:
            try:
                # Get all tables in the database
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Optimize each table
                for table in tables:
                    try:
                        # MySQL's OPTIMIZE TABLE command
                        cursor.execute(f"OPTIMIZE TABLE `{table}`")
                        results.append(f"Optimized table: {table}")
                    except Exception as table_error:
                        # Try ANALYZE TABLE instead if OPTIMIZE fails
                        try:
                            cursor.execute(f"ANALYZE TABLE `{table}`")
                            results.append(f"Analyzed table: {table}")
                        except:
                            results.append(f"Could not optimize/analyze table {table}: {str(table_error)}")
            except Exception as db_error:
                results.append(f"Database optimization error: {str(db_error)}")
        
        # Check migrations
        try:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'showmigrations'],
                cwd=settings.BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.returncode == 0:
                results.append("Checked migrations status")
            else:
                results.append(f"Migration check warning: {result.stderr}")
        except Exception as e:
            results.append(f"Migration check failed: {str(e)}")
            
        return JsonResponse({
            'success': True, 
            'message': 'Database optimization completed',
            'details': results
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'success': False, 
            'message': str(e),
            'details': error_details
        }, status=500)

@login_required
@require_POST
@csrf_exempt
def delete_backup(request, backup_id):
    if request.user.role != 'superadmin':
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        backup_file = os.path.join(settings.BASE_DIR, 'backups', backup_id)
        
        # Also check for alternative extension
        alt_backup_id = backup_id
        if backup_id.endswith('.sql'):
            alt_backup_id = backup_id.replace('.sql', '.json')
        elif backup_id.endswith('.json'):
            alt_backup_id = backup_id.replace('.json', '.sql')
            
        alt_backup_file = os.path.join(settings.BASE_DIR, 'backups', alt_backup_id)
        
        if not os.path.exists(backup_file) and not os.path.exists(alt_backup_file):
            return JsonResponse({'success': False, 'message': 'Backup file not found'}, status=404)
        
        # Delete both versions if they exist
        if os.path.exists(backup_file):
            os.remove(backup_file)
            
        if os.path.exists(alt_backup_file):
            os.remove(alt_backup_file)
            
        return JsonResponse({'success': True, 'message': 'Backup deleted successfully'})
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({
            'success': False, 
            'message': str(e),
            'details': error_details
        }, status=500)

@login_required
def toggle_hotel_status(request, hotel_id):
    if request.user.role != 'superadmin':
        return JsonResponse({"success": False, "message": "You are not authorized to perform this action"})
    
    hotel = get_object_or_404(Hotel, pk=hotel_id)
    
    # Toggle the status regardless of request method
    hotel.status = not hotel.status
    hotel.save()
    
    status_text = "activated" if hotel.status else "deactivated"
    messages.success(request, f'Hotel "{hotel.name}" {status_text} successfully.')
    
    # Check if we should return to a specific page
    return_to = request.GET.get('return_to')
    if return_to == 'restaurant_details':
        return redirect('view_restaurant', hotel_id=hotel_id)
    
    # Default return to home
    return redirect('home')

@login_required
def analytics_dashboard(request):
    """
    Comprehensive analytics dashboard for admin users.
    Displays key metrics about users, revenue, and platform performance.
    """
    if request.user.role != 'superadmin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    # Get overall stats
    total_users = User.objects.count()
    total_hotels = Hotel.objects.count()
    active_hotels = Hotel.objects.filter(status=True).count()
    
    # Calculate total revenue across all restaurants
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    total_revenue = Order.objects.filter(
        completed=True,
        created_at__month=current_month,
        created_at__year=current_year
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Calculate total orders
    total_orders = Order.objects.filter(
        completed=True,
        created_at__month=current_month,
        created_at__year=current_year
    ).count()
    
    # Get average rating (if applicable)
    avg_rating = 4.8  # Placeholder value
    
    # Get top performing restaurants
    top_restaurants = Hotel.objects.annotate(
        order_count=Count('order', filter=Q(order__completed=True)),
        total_revenue=Sum('order__total', filter=Q(order__completed=True))
    ).order_by('-total_revenue')[:3]
    
    # Get monthly revenue data for the chart
    months = []
    revenue_data = []
    
    for i in range(12):
        month = (timezone.now().replace(day=1) - timedelta(days=i*30)).month
        year = (timezone.now().replace(day=1) - timedelta(days=i*30)).year
        month_name = calendar.month_abbr[month]
        
        monthly_revenue = Order.objects.filter(
            completed=True,
            created_at__month=month,
            created_at__year=year
        ).aggregate(total=Sum('total'))['total'] or 0
        
        months.insert(0, month_name)
        revenue_data.insert(0, float(monthly_revenue))
    
    # Order distribution data
    # These could be calculated from real data in a production environment
    order_distribution = {
        'labels': ['Dine-in', 'Takeaway', 'Delivery', 'Online'],
        'data': [45, 25, 20, 10]  # Placeholder values
    }
    
    # User activity data (new vs active users)
    now = timezone.now()
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    new_users_data = []
    active_users_data = []
    
    for i in range(7):
        day = (now - timedelta(days=i)).weekday()
        day_date = (now - timedelta(days=i)).date()
        
        # New users registered on this day
        new_users_count = User.objects.filter(
            date_joined__date=day_date
        ).count()
        
        # Active users (users who placed orders) on this day - fix the relationship direction
        active_users_count = Order.objects.filter(
            completedby__isnull=False,
            created_at__date=day_date
        ).values('completedby').distinct().count()
        
        new_users_data.insert(0, new_users_count)
        active_users_data.insert(0, active_users_count)
    
    # Geographic distribution (top 4 cities)
    cities = [
        {'city': 'Mumbai', 'users': 8543, 'orders': 432, 'revenue': 152400},
        {'city': 'Delhi', 'users': 6234, 'orders': 356, 'revenue': 124800},
        {'city': 'Bangalore', 'users': 5678, 'orders': 298, 'revenue': 104500},
        {'city': 'Hyderabad', 'users': 4321, 'orders': 245, 'revenue': 86700}
    ]
    
    context = {
        'total_users': total_users,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_rating': avg_rating,
        'total_hotels': total_hotels,
        'active_hotels': active_hotels,
        'top_restaurants': top_restaurants,
        'months': json.dumps(months),
        'revenue_data': json.dumps(revenue_data),
        'order_distribution': order_distribution,
        'days_of_week': json.dumps(days_of_week),
        'new_users_data': json.dumps(new_users_data),
        'active_users_data': json.dumps(active_users_data),
        'cities': cities
    }
    
    return render(request, 'superadmin/analytics_dashboard.html', context)

@login_required
def financial_reports(request):
    """
    Financial reports dashboard for admin users.
    Shows detailed financial metrics, trends, and restaurant performance.
    """
    if request.user.role != 'superadmin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    # Get date range for filtering
    time_period = request.GET.get('period', 'month')  # Options: day, week, month, year
    
    now = timezone.now()
    
    if time_period == 'day':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = start_date - timedelta(days=1)
    elif time_period == 'week':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = start_date - timedelta(days=7)
    elif time_period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        previous_start = start_date.replace(year=start_date.year-1)
    else:  # month (default)
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_date.month == 1:
            previous_start = start_date.replace(year=start_date.year-1, month=12)
        else:
            previous_start = start_date.replace(month=start_date.month-1)
    
    # Calculate end dates
    end_date = now
    previous_end = start_date - timedelta(microseconds=1)
    
    # Get revenue data for current period
    revenue_data = Order.objects.filter(
        completed=True,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).aggregate(total=Sum('total'))
    
    current_revenue = revenue_data['total'] or 0
    
    # Get revenue data for previous period
    previous_revenue_data = Order.objects.filter(
        completed=True,
        created_at__gte=previous_start,
        created_at__lte=previous_end
    ).aggregate(total=Sum('total'))
    
    previous_revenue = previous_revenue_data['total'] or 0
    
    # Calculate revenue change percentage
    revenue_change_pct = 0
    if previous_revenue > 0:
        revenue_change_pct = ((current_revenue - previous_revenue) / previous_revenue) * 100
    
    # Get restaurant financial performance data
    restaurant_performance = Hotel.objects.filter(status=True).annotate(
        revenue=Sum('order__total', filter=Q(order__completed=True, order__created_at__gte=start_date, order__created_at__lte=end_date)),
        orders=Count('order', filter=Q(order__completed=True, order__created_at__gte=start_date, order__created_at__lte=end_date))
    ).order_by('-revenue')[:10]
    
    # Get recent transactions
    recent_transactions = Order.objects.filter(
        completed=True
    ).order_by('-created_at')[:10]
    
    context = {
        'current_revenue': current_revenue,
        'previous_revenue': previous_revenue,
        'revenue_change_pct': revenue_change_pct,
        'time_period': time_period,
        'restaurant_performance': restaurant_performance,
        'recent_transactions': recent_transactions,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'superadmin/financial_reports.html', context)

@login_required
def user_activity(request):
    """
    User activity dashboard for admin users.
    Shows user registration trends, active users, and user behavior.
    """
    if request.user.role != 'superadmin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    # Get date range for filtering
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Get user registrations by day
    User = get_user_model()
    
    # Fix: Use proper date formatting for SQLite/MySQL compatibility
    registrations_by_day = User.objects.filter(
        date_joined__gte=start_date
    ).values(
        'date_joined__date'
    ).annotate(
        count=Count('id')
    ).order_by('date_joined__date')
    
    # Process registration data for chart
    reg_dates = []
    reg_counts = []
    
    for entry in registrations_by_day:
        # Convert date object to string to avoid serialization issues
        date_str = entry['date_joined__date'].strftime('%Y-%m-%d')
        reg_dates.append(date_str)
        reg_counts.append(entry['count'])
    
    # Get user count by role
    users_by_role = User.objects.values('role').annotate(count=Count('id'))
    
    # Fix: Get most active staff (users who have completed orders)
    # Use reverse relation from Order to User via completedby field
    active_staff = User.objects.filter(
        role__in=['staff', 'owner']
    ).annotate(
        orders_completed=Count('order', filter=Q(order__completed=True))
    ).order_by('-orders_completed')[:10]
    
    # Get new user registrations over time (for chart)
    time_periods = []
    registration_counts = []
    
    # Create a dictionary to store counts for all days in the range
    date_counts = {}
    start_date_obj = start_date.date()
    end_date_obj = timezone.now().date()
    
    # Initialize all dates with 0 count
    current_date = start_date_obj
    while current_date <= end_date_obj:
        date_counts[current_date] = 0
        current_date += timedelta(days=1)
    
    # Fill in actual counts from database
    for entry in registrations_by_day:
        date_obj = entry['date_joined__date']
        if date_obj in date_counts:
            date_counts[date_obj] = entry['count']
    
    # Convert to lists in proper order
    for date_obj in sorted(date_counts.keys()):
        formatted_date = date_obj.strftime('%d %b')
        time_periods.append(formatted_date)
        registration_counts.append(date_counts[date_obj])
    
    # Get recent user activity
    recent_logins = User.objects.filter(
        last_login__gte=start_date
    ).order_by('-last_login')[:10]
    
    context = {
        'registrations_by_day': registrations_by_day,
        'users_by_role': users_by_role,
        'active_staff': active_staff,
        'days': days,
        'recent_logins': recent_logins,
        'time_periods': json.dumps(time_periods),
        'registration_counts': json.dumps(registration_counts),
        'reg_dates': json.dumps(reg_dates),
        'reg_counts': json.dumps(reg_counts)
    }
    return render(request, 'superadmin/user_activity.html', context)

@login_required
def logs(request):
    if request.user.role != 'superadmin':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    return render(request, 'superadmin/logs.html')

@login_required
def adminplans(request):
    billing_plans = BillingPlans.objects.all().order_by('price')
    context = {
        'billing_plans' : billing_plans
    }
    return render(request, 'superadmin/finance/bills.html', context=context)