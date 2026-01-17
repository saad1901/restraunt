# File Structure & Architecture Reference

## Complete Directory Tree

```
restrauntapp/
│
├── DOCUMENTATION/                  # 📚 Project Documentation (NEW)
│   ├── 00_PROJECT_OVERVIEW.md      # Project overview & key info
│   ├── 01_MODULES_DETAILED.md      # Detailed module documentation
│   ├── 02_FEATURES_COMPLETE.md     # Complete feature list
│   ├── 03_ROLES_PERMISSIONS.md     # User roles & permissions
│   ├── 04_DATABASE_API.md          # Database schema & API endpoints
│   ├── 05_INSTALLATION_DEPLOYMENT.md # Setup & deployment guide
│   └── 06_FILE_STRUCTURE.md        # This file
│
├── app/                            # 🏠 Core Restaurant Module
│   ├── __init__.py
│   ├── admin.py                    # Django admin configuration
│   ├── apps.py                     # App configuration
│   ├── forms.py                    # Django forms
│   ├── models.py                   # Database models (User, Hotel, Order, etc)
│   ├── sendmail.py                 # Email utility functions
│   ├── sendmsg.py                  # SMS utility functions
│   ├── views.py                    # Core views (mostly commented)
│   ├── __pycache__/                # Python cache
│   │
│   ├── migrations/                 # Database migrations
│   │   ├── __init__.py
│   │   ├── 0001_initial.py         # Initial migration
│   │   ├── 0002_order_online_source_order_order_type.py
│   │   ├── 0002_paymentdetails.py
│   │   ├── 0003_alter_order_online_source.py
│   │   ├── 0003_rename_upidid_paymentdetails_upiid.py
│   │   ├── 0004_inventoryitem_inventorytransaction.py
│   │   ├── 0005_merge_20250718_0148.py
│   │   ├── 0006_order_started.py
│   │   ├── 0007_menuitem_active.py
│   │   ├── 0008_menuitem_food_type.py
│   │   ├── 0009_hotel_expiry.py
│   │   ├── 0010_paymentrecord.py
│   │   ├── 0011_paymentrecord_cf_order_id_and_more.py
│   │   ├── 0012_remove_paymentrecord_cf_order_id_and_more.py
│   │   ├── 0013_paymentrecord_payment_link.py
│   │   └── __pycache__/
│   │
│   ├── migrations-aws/             # AWS RDS migration history
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── __pycache__/
│   │
│   ├── templatetags/               # Custom Django template tags
│   │   ├── __init__.py
│   │   ├── inventory_filters.py     # Inventory-related filters
│   │   └── __pycache__/
│   │
│   ├── Views/                      # Additional view files
│   └── __pycache__/
│
├── owner/                          # 👔 Restaurant Owner Module
│   ├── __init__.py
│   ├── admin.py                    # Owner-specific admin
│   ├── apps.py
│   ├── billing.py                  # Billing operations
│   ├── inventory_views.py           # Inventory management views
│   ├── models.py                   # Owner-specific models (currently empty)
│   ├── tests.py
│   ├── urls.py                     # Owner URL routing
│   ├── views.py                    # Main owner views (41 functions)
│   │   ├── Dashboard (owner)
│   │   ├── Order management (submit, complete, delete, update)
│   │   ├── Menu management (categories & items)
│   │   ├── Table management
│   │   ├── Reporting (daily, monthly, revenue, time analysis)
│   │   ├── Staff management
│   │   ├── Payment processing (Cashfree integration)
│   │   ├── Billing & subscription
│   │   └── Profile settings
│   ├── __pycache__/
│   └── migrations/
│       ├── __init__.py
│       └── __pycache__/
│
├── staff/                          # 👨‍🍳 Restaurant Staff Module
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Staff-specific models (empty)
│   ├── tests.py
│   ├── urls.py                     # Staff URL routing
│   ├── views.py                    # Staff views (2 main functions)
│   │   ├── home()                  # Staff dashboard
│   │   └── waiter_active_orders()  # View active orders
│   ├── __pycache__/
│   └── migrations/
│       ├── __init__.py
│       └── __pycache__/
│
├── superadmin/                     # 🛡️ System Administration Module
│   ├── __init__.py
│   ├── admin.py                    # SuperAdmin panel config
│   ├── apps.py
│   ├── models.py                   # BillingPlans model
│   ├── tests.py
│   ├── urls.py                     # SuperAdmin URL routing
│   ├── views.py                    # SuperAdmin views (23 functions)
│   │   ├── User management (add, edit, delete, toggle)
│   │   ├── Restaurant management
│   │   ├── Database operations (backup, restore, optimize)
│   │   ├── System operations (git pull, monitoring)
│   │   ├── Analytics & reporting (system-wide)
│   │   ├── Financial reports
│   │   ├── User activity tracking
│   │   ├── Logs & audit trail
│   │   └── Billing plans management
│   ├── __pycache__/
│   └── migrations/
│       ├── __init__.py
│       ├── 0001_initial.py
│       └── __pycache__/
│
├── authn/                          # 🔐 Authentication Module
│   ├── setupView.py                # Owner/hotel registration views
│   ├── urls.py                     # Auth URL routing
│   ├── views.py                    # Auth views
│   │   ├── owner_login()           # Login page
│   │   ├── logout_user()           # Logout
│   │   └── redirection()           # Role-based routing
│   └── __pycache__/
│
├── frontsite/                      # 🌐 Public Website Module
│   ├── policy_views.py             # Policy pages
│   ├── urls.py                     # FrontSite URL routing
│   ├── views.py                    # Public views
│   │   └── homepage()              # Public homepage
│   └── __pycache__/
│
├── agent/                          # 📊 Agent Management Module
│   ├── urls.py                     # Agent URL routing
│   ├── views.py                    # Agent views
│   │   ├── agenthome()             # Agent dashboard
│   │   └── demo()                  # Demo page
│   └── __pycache__/
│
├── userApp/                        # 📱 Customer App Module
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Customer app models (empty)
│   ├── tests.py
│   ├── views.py                    # Customer views
│   │   └── show_menu()             # Display menu for customers
│   ├── __pycache__/
│   └── migrations/
│       ├── __init__.py
│       └── __pycache__/
│
├── payments/                       # 💳 Payment Processing Module
│   ├── pay_link_customer.py         # Cashfree payment link generation
│   └── __pycache__/
│
├── restrauntapp/                   # ⚙️ Django Project Settings
│   ├── __init__.py
│   ├── asgi.py                     # ASGI configuration (async)
│   ├── settings.py                 # Main Django settings
│   │   ├── Database configuration
│   │   ├── Installed apps
│   │   ├── Middleware
│   │   ├── Templates setup
│   │   └── Static files
│   ├── urls.py                     # Main URL router
│   │   ├── Admin site
│   │   ├── App routes
│   │   ├── Owner routes
│   │   ├── Staff routes
│   │   ├── SuperAdmin routes
│   │   ├── Agent routes
│   │   ├── FrontSite routes
│   │   ├── Auth routes
│   │   ├── Registration routes
│   │   └── Service worker
│   ├── wsgi.py                     # WSGI configuration (production)
│   └── __pycache__/
│
├── templates/                      # 🎨 HTML Templates
│   ├── settings.html               # Settings page
│   │
│   ├── agent/                      # Agent templates
│   │   ├── agent.html              # Agent dashboard
│   │   └── demobyagent.html        # Agent demo
│   │
│   ├── auth/                       # Authentication templates
│   │   ├── login.html              # Login page
│   │   └── (other auth pages)
│   │
│   ├── Baseimages/                 # Base template images
│   │
│   ├── frontsite/                  # Public website templates
│   │   ├── homepage.html
│   │   └── (other public pages)
│   │
│   ├── owner/                      # Owner dashboard templates
│   │   ├── dashboard.html
│   │   ├── orders/                 # Order templates
│   │   ├── menu/                   # Menu templates
│   │   ├── tables/                 # Table templates
│   │   ├── staff/                  # Staff templates
│   │   ├── reports/                # Reports & analytics templates
│   │   │   ├── inventory.html      # Inventory dashboard
│   │   │   ├── daily.html          # Daily transaction report
│   │   │   ├── monthly.html        # Monthly report
│   │   │   └── (other reports)
│   │   ├── billing/                # Billing templates
│   │   └── (other owner pages)
│   │
│   ├── Registration/               # Registration templates
│   │   ├── owner_registration.html
│   │   ├── hotel_registration.html
│   │   └── (other registration)
│   │
│   ├── staff/                      # Staff templates
│   │   ├── dashboard.html
│   │   ├── orders.html             # Active orders view
│   │   └── (other staff pages)
│   │
│   ├── superadmin/                 # SuperAdmin templates
│   │   ├── home.html               # Admin dashboard
│   │   ├── users/                  # User management
│   │   ├── restaurants/            # Restaurant management
│   │   ├── database/               # Database management
│   │   ├── operations/             # System operations
│   │   ├── analytics/              # Analytics dashboard
│   │   ├── reports/                # Financial reports
│   │   └── (other admin pages)
│   │
│   └── usertemplates/              # Customer templates
│       ├── menupage.html           # Customer menu display
│       └── (other customer pages)
│
├── static/                         # 🎭 Static Assets (Development)
│   ├── manifest.json               # PWA manifest
│   ├── css/
│   │   ├── homepage.css            # Homepage styles
│   │   ├── style.css               # Main stylesheet
│   │   └── (other stylesheets)
│   ├── icons/                      # App icons
│   │   ├── favicon.ico
│   │   ├── icon-192.png
│   │   ├── icon-512.png
│   │   └── (other icons)
│   └── js/
│       ├── serviceworker.js        # PWA service worker
│       ├── main.js                 # Main JavaScript
│       ├── dashboard.js            # Dashboard functionality
│       ├── orders.js               # Order management JS
│       └── (other scripts)
│
├── staticfiles/                    # 📦 Collected Static Files (Production)
│   ├── manifest.json
│   ├── admin/                      # Django admin static
│   │   ├── css/
│   │   ├── img/
│   │   └── js/
│   ├── css/
│   │   └── homepage.css
│   ├── js/
│   │   └── serviceworker.js
│   └── (production collected files)
│
├── backups/                        # 📦 Database Backups
│   ├── db_20240101_100000.sqlite3
│   ├── db_20240102_100000.sqlite3
│   └── (periodic backups)
│
├── myapp/                          # 📱 Mobile App (Cordova)
│   ├── config.xml                  # Cordova configuration
│   ├── package.json                # Mobile app dependencies
│   ├── platforms/
│   │   ├── android/                # Android platform
│   │   │   ├── app/build/outputs/apk/
│   │   │   │   └── debug/          # Debug APK
│   │   │   │       └── app-debug.apk
│   │   │   └── (Android build files)
│   │   └── (other platforms)
│   └── www/                        # Mobile app source
│       ├── index.html              # Mobile app entry
│       ├── css/                    # Mobile styles
│       ├── img/                    # Mobile images
│       └── js/                     # Mobile scripts
│
├── db.sqlite3                      # 🗄️ SQLite Database
│
├── manage.py                       # Django management script
│
├── requirements.txt                # Python dependencies
│
├── README.md                       # Project README
│
├── gitpush.py                      # Git automation script
│
├── response.json                   # Response/log file
│
├── testfile.txt                    # Test file
│
├── urls.py                         # (May be duplicate)
│
├── Z-todo.md                       # Todo notes
│
└── .gitignore                      # Git ignore file
```

---

## Module Relationships

```
┌────────────────────────────────────────────────────┐
│         DJANGO PROJECT (restrauntapp)              │
└────────────────────────────────────────────────────┘
                        │
     ┌──────────────────┼──────────────────┐
     │                  │                  │
   Views              URLs                Settings
     │                  │                  │
  (views.py)     (urls.py)          (settings.py)
     │                  │                  │
     └──────────────────┼──────────────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
         Models      Forms      Templates
            │           │           │
        (models.py)  (forms.py)  (templates/)
            │           │           │
         Database    Validation    HTML/CSS
```

### App Dependency Graph

```
restrauntapp (Core Project)
    │
    ├─→ app (Core Models)
    │   ├─→ User, Hotel, Table
    │   ├─→ Menu (Categories, Items)
    │   ├─→ Order (Orders, Items)
    │   ├─→ Payment (PaymentDetails, PaymentRecord)
    │   └─→ Inventory (Items, Transactions)
    │
    ├─→ owner (Depends on: app)
    │   ├─→ Views (Dashboard, Orders, Menu, Staff, Reports, Billing)
    │   ├─→ Inventory Views
    │   └─→ Billing Operations
    │
    ├─→ staff (Depends on: app)
    │   └─→ Views (Active Orders Dashboard)
    │
    ├─→ superadmin (Depends on: app)
    │   ├─→ Views (Admin Dashboard, Users, Database, Analytics)
    │   └─→ Models (BillingPlans)
    │
    ├─→ authn (Depends on: app)
    │   └─→ Views (Login, Logout, Registration)
    │
    ├─→ frontsite (Depends on: app)
    │   └─→ Views (Public Homepage, Menu)
    │
    ├─→ agent (Depends on: app)
    │   └─→ Views (Agent Dashboard)
    │
    ├─→ userApp (Depends on: app)
    │   └─→ Views (Menu Display for Customers)
    │
    └─→ payments (Depends on: app, superadmin)
        └─→ Cashfree Integration
```

---

## Key Files Location

### Configuration Files
| File | Purpose |
|------|---------|
| `restrauntapp/settings.py` | Django settings, database, apps, middleware |
| `restrauntapp/urls.py` | Main URL routing |
| `restrauntapp/wsgi.py` | Production WSGI server |
| `restrauntapp/asgi.py` | Async server |
| `requirements.txt` | Python dependencies |
| `manage.py` | Django management CLI |

### Core Models
| File | Purpose |
|------|---------|
| `app/models.py` | User, Hotel, Table, Menu, Order, Payment, Inventory |
| `superadmin/models.py` | BillingPlans |
| `owner/models.py` | Empty (uses app models) |

### Main Views
| File | Purpose |
|------|---------|
| `owner/views.py` | Owner dashboard & management (41 functions) |
| `owner/inventory_views.py` | Inventory management |
| `superadmin/views.py` | Admin operations (23 functions) |
| `staff/views.py` | Staff dashboard (2 functions) |
| `authn/views.py` | Authentication & login |
| `frontsite/views.py` | Public website |
| `agent/views.py` | Agent dashboard |
| `userApp/views.py` | Customer menu display |

### Forms & Utilities
| File | Purpose |
|------|---------|
| `app/forms.py` | Django forms for all models |
| `app/sendmail.py` | Email utilities |
| `app/sendmsg.py` | SMS utilities (Twilio) |
| `payments/pay_link_customer.py` | Payment gateway functions |
| `owner/billing.py` | Billing operations |

### Database
| File | Purpose |
|------|---------|
| `db.sqlite3` | SQLite database (development) |
| `app/migrations/` | Database schema history |
| `superadmin/migrations/` | Admin schema history |

### Static Files
| Directory | Purpose |
|-----------|---------|
| `static/css/` | Stylesheets |
| `static/js/` | JavaScript files |
| `static/icons/` | App icons & favicon |
| `staticfiles/` | Collected production static files |

### Templates
| Directory | Purpose |
|-----------|---------|
| `templates/owner/` | Owner dashboard templates |
| `templates/superadmin/` | Admin templates |
| `templates/staff/` | Staff templates |
| `templates/auth/` | Login/registration |
| `templates/frontsite/` | Public website |
| `templates/usertemplates/` | Customer menu |

---

## Code Organization Principles

### By Role (Templates & Views)
```
templates/owner/       → /owner/* routes
templates/staff/       → /staff/* routes
templates/superadmin/  → /superadmin/* routes
templates/frontsite/   → /site/* routes
templates/auth/        → /auth/* routes
```

### By Feature (Models)
```
app/models.py:
  - User (authentication)
  - Hotel (multi-tenancy)
  - Table, MenuCategory, MenuItem (menu)
  - Order, OrderItems (orders)
  - PaymentDetails, PaymentRecord (payments)
  - InventoryItem, InventoryTransaction (inventory)
```

### By Function (Views)
```
owner/views.py:
  - Order management (5 functions)
  - Menu management (6 functions)
  - Table management (3 functions)
  - Reporting (6 functions)
  - Staff management (3 functions)
  - Payment/Billing (5 functions)
  - Others (8 functions)
```

---

## File Size Estimates

| Component | Approx Size |
|-----------|-------------|
| Database (db.sqlite3) | 2-10 MB |
| Static files (css/js/icons) | 5-20 MB |
| Source code (all Python) | 2-5 MB |
| Templates (HTML) | 1-3 MB |
| Total project | 15-50 MB |

---

## Important Notes

### Version Control
- `.gitignore` should exclude:
  - `*.pyc`, `__pycache__/`
  - `*.sqlite3` (database)
  - `venv/`, `env/`
  - `.env` (secrets)
  - `staticfiles/`

### Sensitive Data
- Keep `SECRET_KEY` in environment variables
- Store API credentials (Twilio, Cashfree) in `.env`
- Never commit credentials to Git

### Deployment
- Collect static files before deploying: `python manage.py collectstatic`
- Run migrations on new environment: `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Update `DEBUG = False` in production

---

**Documentation Updated:** January 17, 2026
