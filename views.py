from django.http import JsonResponse
from django.db import connection
import os
import json
from datetime import datetime
from django.conf import settings
import subprocess
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def database_management(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    # Get database statistics
    with connection.cursor() as cursor:
        # Get database size
        cursor.execute("""
            SELECT pg_size_pretty(pg_database_size(current_database()))
        """)
        db_size = cursor.fetchone()[0]
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        table_count = cursor.fetchone()[0]
        
        # Get table statistics
        cursor.execute("""
            SELECT 
                relname as name,
                n_live_tup as rows,
                pg_size_pretty(pg_total_relation_size(relid)) as size,
                CASE 
                    WHEN n_live_tup > 1000000 THEN 'critical'
                    WHEN n_live_tup > 100000 THEN 'warning'
                    ELSE 'healthy'
                END as status
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
        """)
        table_stats = [
            {
                'name': row[0],
                'rows': row[1],
                'size': row[2],
                'status': row[3]
            }
            for row in cursor.fetchall()
        ]
        
        # Get query performance data (last 24 hours)
        cursor.execute("""
            SELECT 
                date_trunc('hour', query_start) as hour,
                AVG(EXTRACT(EPOCH FROM (query_end - query_start)) * 1000) as avg_duration
            FROM pg_stat_statements
            WHERE query_start >= NOW() - INTERVAL '24 hours'
            GROUP BY hour
            ORDER BY hour
        """)
        query_data = cursor.fetchall()
        query_times = [row[0].strftime('%H:%M') for row in query_data]
        query_durations = [round(row[1], 2) for row in query_data]
        
        # Get daily query count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_stat_statements 
            WHERE query_start >= NOW() - INTERVAL '24 hours'
        """)
        query_count = cursor.fetchone()[0]
    
    # Get backup information
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.sql'):
                filepath = os.path.join(backup_dir, filename)
                backups.append({
                    'id': filename,
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'created_at': datetime.fromtimestamp(os.path.getctime(filepath))
                })
    
    # Get last backup time
    last_backup = backups[0]['created_at'] if backups else None
    
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
    
    return render(request, 'Admin/database_management.html', context)

@require_POST
@csrf_exempt
def create_backup(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sql')
        
        # Create backup using pg_dump
        db_settings = settings.DATABASES['default']
        cmd = [
            'pg_dump',
            '-h', db_settings['HOST'],
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', backup_file
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        subprocess.run(cmd, env=env, check=True)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@csrf_exempt
def restore_backup(request, backup_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        backup_file = os.path.join(settings.BASE_DIR, 'backups', backup_id)
        if not os.path.exists(backup_file):
            return JsonResponse({'success': False, 'message': 'Backup file not found'})
        
        # Restore backup using psql
        db_settings = settings.DATABASES['default']
        cmd = [
            'psql',
            '-h', db_settings['HOST'],
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', backup_file
        ]
        
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        subprocess.run(cmd, env=env, check=True)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@csrf_exempt
def delete_backup(request, backup_id):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        backup_file = os.path.join(settings.BASE_DIR, 'backups', backup_id)
        if not os.path.exists(backup_file):
            return JsonResponse({'success': False, 'message': 'Backup file not found'})
        
        os.remove(backup_file)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
@csrf_exempt
def optimize_database(request):
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Unauthorized'})
    
    try:
        with connection.cursor() as cursor:
            # Vacuum analyze all tables
            cursor.execute("VACUUM ANALYZE")
            
            # Reindex all tables
            cursor.execute("REINDEX DATABASE " + settings.DATABASES['default']['NAME'])
            
            # Update statistics
            cursor.execute("ANALYZE")
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}) 