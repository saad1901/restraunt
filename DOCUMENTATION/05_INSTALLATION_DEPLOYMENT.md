# Installation, Setup & Deployment Guide

## PREREQUISITES

### System Requirements
- **OS:** Linux/Mac/Windows
- **Python:** 3.8+ (Recommended: 3.10+)
- **Database:** SQLite3 (built-in) or MySQL/PostgreSQL
- **RAM:** 2GB minimum
- **Disk Space:** 1GB minimum
- **Browser:** Modern web browser (Chrome, Firefox, Safari, Edge)

### Required Software
```bash
- Python 3.8+
- pip (Python package manager)
- Git (for version control)
- Virtual Environment (venv)
- SQLite3 (pre-installed on most systems)
```

---

## LOCAL INSTALLATION GUIDE

### Step 1: Clone Repository
```bash
git clone <repository_url>
cd restrauntapp
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Settings
Edit `restrauntapp/settings.py`:
```python
# Line 25: Set DEBUG mode
DEBUG = True  # For development

# Line 26: Add allowed hosts
ALLOWED_HOSTS = ['*']  # Or specific domain

# Line 75-84: Database configuration (default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Step 5: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superadmin User
```bash
python manage.py createsuperuser
# Follow prompts to create superadmin account
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

### Step 8: Access Application
```
http://localhost:8000/
```

---

## FIRST-TIME SETUP

### Initial Login
1. Go to `http://localhost:8000/`
2. Login with superadmin credentials created above
3. Auto-redirects to `/superadmin/home/`

### Create Test Owner
1. Go to `http://localhost:8000/register/owner/`
2. Fill in:
   - Username: testowner
   - Email: owner@test.com
   - Password: Test@123456
   - Phone: 9876543210
   - City: Bangalore
   - Hint: test
3. Submit → Redirects to hotel registration

### Create Test Restaurant
1. Fill in:
   - Name: Test Restaurant
   - Address: 123 Main St
2. Submit → Auto-login and redirect to dashboard

### Create Test Staff
1. In owner dashboard → Staff → Add Staff
2. Fill in:
   - Username: teststaff
   - Password: Staff@123
   - Phone: 9876543211
   - Role: Staff
3. Submit

### Create Test Menu
1. In owner dashboard → Menu → Add Category
2. Create categories: Appetizers, Main Course, Desserts
3. Add menu items to each category

### Create Test Tables
1. In owner dashboard → Tables → Add Table
2. Create: Table 1, Table 2, Table 3, etc.

---

## DATABASE SETUP

### SQLite (Default - Development)
```bash
# Already configured in settings.py
# Database file: db.sqlite3

# Backup
cp db.sqlite3 db.sqlite3.backup

# Reset database
rm db.sqlite3
python manage.py migrate
```

### MySQL (Production)
Edit `restrauntapp/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'restaurantdb',
        'USER': 'admin',
        'PASSWORD': 'your_password',
        'HOST': 'your_host',
        'PORT': '3306',
    }
}
```

Install MySQL driver:
```bash
pip install mysqlclient
```

### PostgreSQL (Production)
Edit `restrauntapp/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'restaurantdb',
        'USER': 'admin',
        'PASSWORD': 'your_password',
        'HOST': 'your_host',
        'PORT': '5432',
    }
}
```

Install PostgreSQL driver:
```bash
pip install psycopg2
```

---

## STATIC FILES CONFIGURATION

### Development
Static files are served automatically by Django dev server.

### Production
```bash
# Collect static files
python manage.py collectstatic --noinput

# Files collected to: staticfiles/
# Update web server to serve from staticfiles/
```

### Settings for Production
```python
# restrauntapp/settings.py
DEBUG = False
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

---

## THIRD-PARTY INTEGRATIONS SETUP

### Twilio SMS Integration

1. **Create Twilio Account**
   - Visit: https://www.twilio.com
   - Sign up for free account

2. **Get Credentials**
   - Account SID
   - Auth Token
   - Phone Number

3. **Add to Settings** (Create `.env` or update settings.py)
```python
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"
```

4. **Usage in Code**
```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
message = client.messages.create(
    body="Your order is ready!",
    from_=TWILIO_PHONE_NUMBER,
    to="+919876543210"
)
```

### Cashfree Payment Integration

1. **Create Cashfree Account**
   - Visit: https://cashfree.com
   - Sign up for merchant account
   - Enable Test mode

2. **Get API Credentials**
   - App ID
   - Secret Key

3. **Add to Settings**
```python
CASHFREE_APP_ID = "your_app_id"
CASHFREE_SECRET_KEY = "your_secret_key"
CASHFREE_API_URL = "https://api.cashfree.com/pg/orders"
```

4. **Configure Webhook**
   - In Cashfree dashboard
   - Add webhook URL: `https://yourdomain.com/owner/payments/webhook/`
   - Select events: Payment status updates

5. **Implementation in Code**
```python
# View: owner/views.py - get_payment()
# Already integrated - just add credentials
```

---

## DEPLOYMENT OPTIONS

### Option 1: PythonAnywhere (Current)
Current deployment platform - Application is live at:
```
https://hotelsoftware.pythonanywhere.com/
```

**Setup Steps:**
1. Sign up at pythonanywhere.com
2. Create web app
3. Upload code via Git
4. Configure virtual environment
5. Set WSGI configuration
6. Add domain
7. Enable HTTPS
8. Set environment variables

### Option 2: Heroku

```bash
# 1. Create Procfile
web: gunicorn restrauntapp.wsgi

# 2. Create runtime.txt
python-3.10.10

# 3. Install Gunicorn
pip install gunicorn

# 4. Deploy
heroku create your-app-name
git push heroku main

# 5. Run migrations
heroku run python manage.py migrate
```

### Option 3: AWS (EC2 + RDS)

```bash
# 1. Launch EC2 instance
# 2. Install dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql-client

# 3. Clone repository
git clone <repo_url>

# 4. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Configure RDS
# Create RDS MySQL instance
# Update DATABASES in settings.py

# 6. Run migrations
python manage.py migrate

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Start server (Gunicorn)
gunicorn restrauntapp.wsgi:application --bind 0.0.0.0:8000
```

### Option 4: Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "restrauntapp.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t restaurant-app .
docker run -p 8000:8000 restaurant-app
```

---

## ENVIRONMENT VARIABLES

Create `.env` file in project root:
```
DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
CASHFREE_APP_ID=your_cashfree_app_id
CASHFREE_SECRET_KEY=your_cashfree_secret
```

Load in settings.py:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

---

## SECURITY CHECKLIST

### Pre-Production
- [ ] Set `DEBUG = False`
- [ ] Update `SECRET_KEY` (use strong random value)
- [ ] Set `ALLOWED_HOSTS` to specific domains
- [ ] Enable HTTPS
- [ ] Configure CSRF_TRUSTED_ORIGINS
- [ ] Set secure cookie flags
- [ ] Enable security middleware
- [ ] Update CORS settings if needed
- [ ] Hide sensitive environment variables
- [ ] Create strong superadmin password
- [ ] Backup database
- [ ] Test payment gateway in production mode

### Settings for Production
```python
DEBUG = False
SECRET_KEY = 'your-very-long-random-secret-key'
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = { ... }
X_FRAME_OPTIONS = 'DENY'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Use production RDS/managed database
    }
}
```

---

## MAINTENANCE TASKS

### Regular Backups
```bash
# SQLite backup
cp db.sqlite3 backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# Full project backup
tar -czf backups/project_$(date +%Y%m%d).tar.gz .
```

### Database Optimization
```bash
# Access SuperAdmin → Database Management
# Or via command:
python manage.py sqlsequencereset app superadmin owner staff userApp | python manage.py dbshell
```

### Update Dependencies
```bash
pip list --outdated
pip install -U package_name
pip freeze > requirements.txt
```

### Log Rotation
Configure log rotation for production logs to prevent disk space issues.

### Performance Monitoring
- Monitor server logs
- Check database query performance
- Monitor disk space usage
- Monitor memory usage
- Track error rates

---

## TROUBLESHOOTING

### Common Issues

#### 1. Migration Errors
```bash
# Reset migrations (development only!)
python manage.py migrate app zero
python manage.py migrate

# Or create fresh database
rm db.sqlite3
python manage.py migrate
```

#### 2. Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check STATIC_ROOT and STATIC_URL in settings.py
```

#### 3. Database Connection Error
```bash
# Check database settings
python manage.py dbshell

# Or verify credentials for RDS/external database
```

#### 4. Payment Gateway Webhook Not Working
- Verify webhook URL is publicly accessible
- Check firewall/security group rules
- Verify signature key matches
- Check logs for errors

#### 5. Email/SMS Not Sending
- Verify Twilio credentials
- Check phone number format
- Ensure API quotas not exceeded
- Check firewall rules for outbound connections

#### 6. Login Issues
- Clear cookies/cache
- Reset superadmin password
- Check user role and permissions
- Verify session settings

---

## PERFORMANCE OPTIMIZATION

### Database Optimization
- Add indexes on frequently queried fields
- Use select_related() for foreign keys
- Use prefetch_related() for reverse relations
- Paginate large result sets
- Archive old orders/transactions

### Caching
```python
# Add caching to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Use in views
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def menu_view(request):
    pass
```

### Query Optimization
- Use aggregation for summaries
- Batch operations together
- Reduce N+1 queries
- Use transaction decorators

### Frontend Optimization
- Minify CSS/JavaScript
- Compress images
- Enable gzip compression
- Use CDN for static files
- Lazy load images

---

## MOBILE APP SETUP

### Android APK Building
```bash
# If using Cordova framework
cordova platform add android
cordova build android

# APK location: platforms/android/app/build/outputs/apk/debug/

# For release:
cordova build android --release
```

### App Permissions
Update `config.xml` with required permissions:
```xml
<permission name="android.permission.INTERNET" />
<permission name="android.permission.ACCESS_NETWORK_STATE" />
<permission name="android.permission.CAMERA" />
<permission name="android.permission.READ_PHONE_STATE" />
```

---

## BACKUP & RECOVERY

### Create Backup
Via SuperAdmin Dashboard:
1. Go to Database Management
2. Click "Create Backup"
3. Backup automatically saved with timestamp

### Restore Backup
Via SuperAdmin Dashboard:
1. Go to Database Management
2. Select backup from list
3. Click "Restore"
4. System creates pre-restore backup automatically

### Manual Backup
```bash
# SQLite
python manage.py dumpdata > backup.json

# Restore
python manage.py loaddata backup.json
```

---

## SUPPORT & RESOURCES

- **Django Documentation:** https://docs.djangoproject.com/
- **PythonAnywhere Help:** https://www.pythonanywhere.com/help/
- **Cashfree API Docs:** https://developer.cashfree.com/
- **Twilio API Docs:** https://www.twilio.com/docs/

---

**Documentation Updated:** January 17, 2026
