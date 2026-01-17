# Quick Reference Guide

## Documentation Index

### 📚 Complete Documentation Files

1. **[00_PROJECT_OVERVIEW.md](00_PROJECT_OVERVIEW.md)**
   - Project description and purpose
   - Technology stack and dependencies
   - System architecture
   - Core applications overview
   - Database models summary
   - URL routing structure

2. **[01_MODULES_DETAILED.md](01_MODULES_DETAILED.md)**
   - In-depth module documentation
   - Each module's purpose and features
   - All views and functions explained
   - Feature implementations
   - Code patterns and examples

3. **[02_FEATURES_COMPLETE.md](02_FEATURES_COMPLETE.md)**
   - Complete feature list
   - Feature descriptions by category
   - Feature matrix by user role
   - Advanced features
   - Future enhancement possibilities

4. **[03_ROLES_PERMISSIONS.md](03_ROLES_PERMISSIONS.md)**
   - User roles and access levels
   - Detailed permissions for each role
   - Permission matrix
   - Access control implementation
   - URL access patterns

5. **[04_DATABASE_API.md](04_DATABASE_API.md)**
   - Database schema with all fields
   - Table relationships and ERD
   - API endpoints documentation
   - Payment gateway integration
   - Query optimization patterns

6. **[05_INSTALLATION_DEPLOYMENT.md](05_INSTALLATION_DEPLOYMENT.md)**
   - Local installation steps
   - Database setup (SQLite, MySQL, PostgreSQL)
   - Third-party integrations setup
   - Deployment options (PythonAnywhere, Heroku, AWS, Docker)
   - Security checklist
   - Troubleshooting guide

7. **[06_FILE_STRUCTURE.md](06_FILE_STRUCTURE.md)**
   - Complete directory tree
   - Module relationships
   - Key files location
   - Code organization principles
   - Deployment requirements

---

## Quick Start

### Installation (5 minutes)
```bash
git clone <repo_url>
cd restrauntapp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Access:** http://localhost:8000/

### First Login
- Create superuser: `python manage.py createsuperuser`
- Login with created credentials
- Create test owner and restaurant
- Add menu items and tables
- Create test staff members

---

## Database Models Quick Reference

```
User (Custom) ─┐
             ├─> Hotel
             ├─> Staff Assignment
             ├─> Orders
             ├─> Payments
             └─> Inventory Transactions

Hotel ─────────> Table
             ├─> Menu Categories
             ├─> Menu Items
             ├─> Orders
             ├─> Inventory Items
             └─> Payment Details

Order ─────────> Order Items → Menu Items
             ├─> Tables
             └─> Payment Records

InventoryItem ─> Inventory Transactions
```

---

## API Endpoints Summary

### Authentication
- `POST /auth/login/` - Login
- `GET /auth/logout/` - Logout
- `POST /register/owner/` - Owner registration
- `POST /register/hotel/` - Hotel registration

### Orders
- `POST /owner/orders/submit/` - Create order
- `POST /owner/orders/complete/` - Complete order
- `POST /owner/orders/update-qty/` - Update quantities
- `GET /owner/orders/ajax-get/` - Get active orders

### Menu
- `POST /owner/menu/category/add/` - Add category
- `POST /owner/menu/item/add/` - Add menu item
- `GET /user/getmenu/<hotel_id>/` - Get menu (customer)

### Inventory
- `GET /owner/inventory/` - View inventory
- `POST /owner/inventory/add/` - Add item
- `POST /owner/inventory/transactions/add/` - Record transaction

### Payments
- `GET /owner/payments/link/<plan_id>/` - Generate payment link
- `POST /owner/payments/webhook/` - Payment webhook

---

## User Roles Summary

| Role | Access | Main Functions |
|------|--------|-----------------|
| **SuperAdmin** | All | User mgmt, Database, Analytics |
| **Owner** | Own restaurant | Orders, Menu, Staff, Reports |
| **Staff** | Assigned restaurant | View orders, assist |
| **Agent** | Assigned restaurants | View sales, performance |
| **Customer** | Public menu | Browse menu, place orders |

---

## Key Features Checklist

### Order Management ✓
- Create orders (table/online)
- Update quantities
- Apply discounts
- Mark started/completed
- Delete orders
- Real-time AJAX updates

### Menu Management ✓
- Categories and items
- Price management
- Food type classification
- Active/inactive toggle

### Inventory Management ✓
- Stock tracking
- Multiple units
- Transaction audit trail
- Automatic status
- Reorder level alerts

### Reporting ✓
- Daily transactions
- Monthly reports
- Revenue tracking
- Peak hours analysis
- Custom period reports

### Payments ✓
- UPI integration
- Cashfree gateway
- Subscription billing
- Payment history
- Webhook verification

### Multi-tenancy ✓
- Complete data isolation
- Per-restaurant settings
- Agent management
- Independent operations

---

## Configuration Files

### Main Settings
```
restrauntapp/settings.py
├── Database: SQLite (dev), RDS (prod)
├── Installed apps: 8 main apps
├── Middleware: CSRF, Auth, Sessions
├── Templates: templates/ directory
└── Static files: static/ directory
```

### URLs
```
restrauntapp/urls.py
├── Admin: /admin/
├── Owner: /owner/
├── Staff: /staff/
├── SuperAdmin: /superadmin/
├── Auth: /auth/
├── Public: /site/
└── Mobile: /user/
```

---

## Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Update `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup database (RDS)
- [ ] Configure HTTPS
- [ ] Collect static files
- [ ] Create superuser
- [ ] Setup Twilio credentials
- [ ] Setup Cashfree credentials
- [ ] Configure payment webhook URL
- [ ] Backup database
- [ ] Enable database monitoring
- [ ] Setup logging

---

## Common Commands

### Development
```bash
# Run server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### Production
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn restrauntapp.wsgi:application --bind 0.0.0.0:8000

# Database backup
python manage.py dumpdata > backup.json

# Database restore
python manage.py loaddata backup.json
```

---

## Troubleshooting Guide

### Login Issues
1. Check user exists: `python manage.py shell → User.objects.all()`
2. Check role: `user.role` should be owner/superadmin/etc
3. Clear cookies and try again

### Order Not Saving
1. Check hotel exists: `user.staffof` must be set for staff
2. Check table exists: if table order, table must exist
3. Verify prices are set for menu items

### Payment Not Working
1. Check Cashfree credentials in settings
2. Verify webhook URL in Cashfree dashboard
3. Check signature verification logic
4. Test with Cashfree test mode

### Database Issues
1. Migrations not applied: `python manage.py migrate`
2. Schema mismatch: Review migration files
3. Foreign key errors: Check related objects exist

### Static Files Not Loading
1. Run collectstatic: `python manage.py collectstatic`
2. Check STATIC_ROOT and STATIC_URL
3. Verify web server serves staticfiles/

---

## Performance Tips

1. **Database**
   - Use `select_related()` for ForeignKeys
   - Use `prefetch_related()` for reverse relations
   - Add indexes on frequently queried fields

2. **Caching**
   - Cache menu categories (rarely change)
   - Cache billing plans
   - Use Redis for session storage

3. **Frontend**
   - Minify CSS/JavaScript
   - Compress images
   - Enable gzip compression

4. **Queries**
   - Avoid N+1 queries
   - Use aggregation for sums
   - Paginate large result sets

---

## Security Best Practices

1. **Authentication**
   - Use strong passwords
   - Enable CSRF protection
   - Use secure cookies (HTTPS)

2. **Database**
   - Never expose credentials
   - Use environment variables
   - Regular backups

3. **API**
   - Verify payment signatures
   - Validate input data
   - Use HTTPS for all requests

4. **Code**
   - Sanitize user input
   - Use Django ORM (prevents SQL injection)
   - Check permissions in views

---

## Contact & Support

- **Live Application:** https://hotelsoftware.pythonanywhere.com/
- **Mobile APK:** https://median.co/share/zjembl#apk
- **Framework:** Django 5.2.6
- **Python:** 3.8+

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Aug 2025 | Initial release |
| Current | Jan 2026 | Active development |

---

## Additional Resources

- **Django Docs:** https://docs.djangoproject.com/
- **Cashfree API:** https://developer.cashfree.com/
- **Twilio SDK:** https://www.twilio.com/docs/
- **PythonAnywhere:** https://www.pythonanywhere.com/help/

---

## Documentation Statistics

- **Total Files:** 7 markdown files
- **Total Pages:** ~50 pages of documentation
- **Modules Documented:** 9 apps
- **Models Documented:** 11 core models
- **Views Documented:** 90+ view functions
- **APIs Documented:** 25+ endpoints

---

**Last Updated:** January 17, 2026  
**Documentation Status:** Complete  
**Ready for:** Development, Testing, Production Deployment

