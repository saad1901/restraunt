# Restaurant Management System - Complete Documentation

## Project Overview

**Project Name:** Restaurant Management System  
**Framework:** Django (Python Web Framework)  
**Version:** 5.0.4  
**Database:** SQLite3 (with AWS RDS MySQL/PostgreSQL capability)  
**Deployment:** PythonAnywhere  
**Live Application:** https://hotelsoftware.pythonanywhere.com/  
**Last Updated:** Feb 13, 2026  

---

## Purpose & Objectives

The Restaurant Management System is a comprehensive, multi-role platform designed to streamline restaurant operations through:
- Real-time order tracking and processing
- Menu and table management
- Staff coordination and role-based access control
- Inventory management
- Financial reporting and analytics
- Payment processing and billing
- Agent-based restaurant onboarding
- Superadmin system operations and monitoring

---

## Technology Stack

### Backend
- **Framework:** Django 5.2.6
- **Language:** Python
- **Database:** SQLite3 (Development), MySQL/PostgreSQL (Production via AWS RDS)
- **Authentication:** Django built-in with custom User model
- **API Services:** Twilio (SMS), Cashfree (Payment Processing)

### Frontend
- **HTML/CSS/JavaScript** - Responsive web interface
- **Bootstrap/CSS** - UI styling and layout
- **JavaScript:** AJAX for dynamic interactions
- **Service Worker:** PWA capability with offline support

### Mobile
- **Cordova Framework** - Cross-platform mobile app
- **Android APK** - Android application (~25 MB)
- **Minimum Android Version:** API Level 23 (Android 6.0)

### Dependencies
```
Django==5.2.6
django-widget-tweaks==1.5.0
Twilio==9.8.0
requests==2.32.5
PyJWT==2.10.1
aiohttp==3.12.15
sqlparse==0.5.3
certifi==2025.8.3
```

---

## System Architecture

### Multi-Role System
```
┌─────────────────────────────────────────────────────────────┐
│                    RESTAURANT APP SYSTEM                    │
└─────────────────────────────────────────────────────────────┘
                               │
        ┌──────────┬──────────┬┴──────────┬──────────┬──────────┐
        │          │          │           │          │          │
     SUPERADMIN   AGENT     OWNER       STAFF      USER      OWNER
       ADMIN     MANAGER   (Manager)   (Waiter)  (Customer)  (Billing)
```

---

## Core Applications & Modules

### 1. **app** (Core Restaurant Module)
**Purpose:** Central restaurant operations hub  
**Models:**
- User (Custom Django User Model)
- Hotel (Restaurant entity)
- Table (Dining tables)
- MenuCategory (Menu sections)
- MenuItem (Individual dishes)
- Order (Customer orders)
- OrderItems (Items in an order)
- PaymentDetails (UPI payment information)
- InventoryItem (Stock management)
- InventoryTransaction (Stock movement records)
- PaymentRecord (Payment transaction logs)

**Key Features:**
- User authentication & authorization
- Hotel/Restaurant management
- Menu management
- Table management
- Order management
- Payment details storage

---

### 2. **owner** (Restaurant Owner Module)
**Purpose:** Management interface for restaurant owners  
**Main Views & Features:**

#### Order Management
- `owner()` - Dashboard view showing active orders
- `submit_order()` - Create new orders
- `complete_order()` - Mark orders as completed
- `delete_order()` - Remove orders
- `update_quantity()` - Adjust order item quantities
- `set_order_started()` - Mark order as being prepared (cooking started)
- `ajax_get_orders()` - AJAX endpoint for order updates

#### Menu Management
- `add_category()` - Create menu categories
- `edit_category()` - Modify categories
- `delete_category()` - Remove categories
- `add_menu_item()` - Add new menu items
- `edit_menu_item()` - Update menu items
- `delete_menu_item()` - Remove menu items

#### Table Management
- `add_table()` - Create new tables
- `edit_table()` - Modify table details
- `delete_table()` - Remove tables

#### Reporting & Analytics
- `sales()` - Sales overview
- `dailytransc()` - Daily transaction reports
- `monthly_report()` - Monthly revenue analysis
- `revenue()` - Revenue tracking
- `timeanalysis()` - Peak hours and traffic analysis
- `custom_period()` - Custom date range reports
- `reports()` - Report dashboard

#### Staff Management
- `staff()` - View all staff members
- `add_staff()` - Hire new staff
- `edit_staff()` - Update staff information
- `delete_staff()` - Remove staff members

#### Billing & Payments
- `payment()` - Payment management view
- `owner_billing()` - Billing overview
- `afterpay()` - Subscription management
- `get_payment()` - Payment gateway integration
- `verify_signature()` - Payment verification
- `cashfree_webhook()` - Payment webhook handler
- `bill_history()` - Payment history
- `hotel_profile()` - Restaurant profile settings

#### Inventory Management
- `inventory()` - Inventory dashboard with filters
- `add_inventory_item()` - Add stock items
- `edit_inventory_item()` - Modify stock
- `delete_inventory_item()` - Remove items
- `add_transaction()` - Record inventory movements
- `view_transactions()` - Inventory transaction history

---

### 3. **staff** (Restaurant Staff Module)
**Purpose:** Interface for waiters and kitchen staff  
**Views:**
- `home()` - Staff dashboard
- `waiter_active_orders()` - Active orders for servers

**Features:**
- View active orders
- Check order status
- Process order completions

---

### 4. **superadmin** (System Administration Module)
**Purpose:** Platform administration and system management  
**Main Views & Features:**

#### User Management
- `home()` - Admin dashboard
- `users()` - User list management
- `addagent()` - Create new agents
- `delete_user()` - Remove users
- `view_user()` - User details
- `edit_user()` - Update user information
- `toggle_user_status()` - Activate/deactivate users

#### Restaurant Management
- `view_restaurant()` - View restaurant details
- `toggle_hotel_status()` - Enable/disable restaurants
- System operations for restaurants

#### System Operations
- `system_operations()` - Monitoring dashboard
- `git_pull()` - Git repository updates

#### Database Management
- `database_management()` - DB administration panel
- `create_backup()` - Create database backups
- `restore_backup()` - Restore from backups
- `delete_backup()` - Remove old backups
- `optimize_database()` - Database optimization
- `convert_sql_backups_to_json()` - Backup format conversion

#### Analytics & Reporting
- `analytics_dashboard()` - System-wide analytics
- `financial_reports()` - Overall financial metrics
- `user_activity()` - User activity tracking
- `logs()` - System logs
- `adminplans()` - Billing plans management
- `delete_plan()` - Remove billing plans

---

### 5. **authn** (Authentication Module)
**Purpose:** User authentication and registration  
**Views:**
- `owner_login()` - Owner login page
- `logout_user()` - User logout
- `redirection()` - Role-based redirection after login
- `owner_register()` - Owner registration
- `hotel_register()` - Restaurant registration

**Features:**
- User login/logout
- Role-based access control (RBAC)
- Automatic redirection based on user role
- Registration for owners and restaurants

---

### 6. **frontsite** (Public Website Module)
**Purpose:** Public-facing website for customers  
**Views:**
- `homepage()` - Public homepage with popular items

**Features:**
- Menu browsing
- Restaurant information
- Customer-facing interface

---

### 7. **agent** (Agent/Partner Module)
**Purpose:** Restaurant agent management interface  
**Views:**
- `agenthome()` - Agent dashboard
- `demo()` - Demo page

**Features:**
- View assigned restaurants
- Track total sales from managed restaurants
- Agent-specific analytics

---

### 8. **userApp** (Customer Mobile App Module)
**Purpose:** Mobile app menu interface for customers  
**Views:**
- `show_menu()` - Display restaurant menu

**Features:**
- View menu by restaurant
- Table-specific menu display
- Menu categories and items
- Mobile-optimized interface

---

### 9. **superadmin** (Billing Plans Module)
**Models:**
- BillingPlans - Subscription plans configuration

**Features:**
- Plan creation and management
- Pricing configuration
- Expiry date management
- Active/inactive plan toggling

---

## Database Models & Relationships

```
User (Custom)
├── id
├── username, email, password
├── first_name, last_name
├── phone, city, hint
├── role (superadmin, admin, agent, owner, staff)
├── staffof (ForeignKey: Hotel)
└── is_active, is_staff

Hotel
├── id
├── name, address
├── owner (ForeignKey: User)
├── agent (ForeignKey: User - nullable)
├── status (Boolean)
├── expiry (Date)
└── created_at

Table
├── id
├── hotel (ForeignKey: Hotel)
├── name
├── occupied (Boolean)
└── created_at

MenuCategory
├── id
├── hotel (ForeignKey: Hotel)
├── name
├── icon
└── created_at

MenuItem
├── id
├── hotel (ForeignKey: Hotel)
├── category (ForeignKey: MenuCategory)
├── name
├── price (Decimal)
├── active (Boolean)
├── food_type (veg/non-veg)
└── created_at

Order
├── id
├── hotel (ForeignKey: Hotel)
├── table (ForeignKey: Table - nullable)
├── created_at
├── total (Decimal)
├── discount (Decimal)
├── completed (Boolean)
├── started (Boolean - cooking status)
├── phone_number
├── completedby (ForeignKey: User)
├── order_type (table/online)
├── online_source (swiggy/zomato/free/other)
└── created_at

OrderItems
├── id
├── hotel (ForeignKey: Hotel)
├── item (ForeignKey: MenuItem)
├── order (ForeignKey: Order)
├── quantity (Integer)
└── created_at

PaymentDetails
├── id
├── hotel (ForeignKey: Hotel)
├── upiid
├── name
└── created_at

InventoryItem
├── id
├── hotel (ForeignKey: Hotel)
├── name
├── description
├── quantity (Decimal)
├── unit (kg/g/l/ml/pcs/pkg/box)
├── unit_price (Decimal)
├── reorder_level (Decimal)
├── status (in_stock/low_stock/out_of_stock)
├── category (ForeignKey: MenuCategory - nullable)
├── last_updated
└── created_at

InventoryTransaction
├── id
├── hotel (ForeignKey: Hotel)
├── item (ForeignKey: InventoryItem)
├── transaction_type (purchase/usage/adjustment/writeoff)
├── quantity (Decimal)
├── transaction_date
├── notes
├── created_by (ForeignKey: User)
├── unit_price (Decimal - nullable)
└── created_at

PaymentRecord
├── id
├── user (ForeignKey: User)
├── hotel (ForeignKey: Hotel)
├── order_id (unique)
├── amount (Decimal)
├── status (PENDING/SUCCESS/FAILED)
├── payment_link
└── created_at

BillingPlans
├── id
├── name (unique)
├── price (Integer)
├── active (Boolean)
├── description
├── expiry_days (Integer)
└── created_at
```

---

## URL Routing Structure

```
┌────────────────────────── owner_login (home)
├── owner/ ──────────────── owner module urls
│   ├── orders/
│   ├── menu/
│   ├── tables/
│   ├── staff/
│   ├── reports/
│   ├── inventory/
│   └── billing/
│
├── staff/ ───────────────── staff module urls
│   └── orders/
│
├── superadmin/ ──────────── superadmin module urls
│   ├── users/
│   ├── restaurants/
│   ├── database/
│   ├── analytics/
│   └── operations/
│
├── agent/ ───────────────── agent module urls
│   └── dashboard/
│
├── site/ ────────────────── frontsite module urls
│   └── homepage/
│
├── auth/ ────────────────── authentication urls
│   ├── login/
│   ├── logout/
│   └── register/
│
├── register/
│   ├── owner/ ─────────── Owner registration
│   └── hotel/ ─────────── Restaurant registration
│
├── admin/ ──────────────── Django admin panel
│
├── user/
│   └── getmenu/<hotel_id>/<table_id>/ ── Customer menu view
│
└── serviceworker.js ────── PWA service worker
```

---

## User Roles & Permissions

### 1. **SuperAdmin**
- **Access:** Complete system control
- **Capabilities:**
  - User management (create, edit, delete, toggle status)
  - Restaurant management (view, enable/disable)
  - System operations and monitoring
  - Database backup, restore, optimization
  - Analytics and financial reports
  - Billing plans management
  - Logs and activity tracking

### 2. **Agent**
- **Access:** Assigned restaurants only
- **Capabilities:**
  - View assigned restaurants
  - Track sales metrics from managed restaurants
  - Demo functionality

### 3. **Owner**
- **Access:** Own restaurant only
- **Capabilities:**
  - Order management (create, complete, delete, update)
  - Menu management (categories, items)
  - Table management
  - Staff management
  - Sales and revenue reporting
  - Inventory management
  - Payment processing and billing
  - UPI payment configuration

### 4. **Staff (Waiter)**
- **Access:** Their restaurant only
- **Capabilities:**
  - View active orders
  - Check order status
  - Assist in order processing

### 5. **User (Customer)**
- **Access:** Public menu view
- **Capabilities:**
  - Browse menu
  - View items by category
  - Place orders (table or online)

---

## Key Features

### 1. **Order Management**
- Create table/online orders
- Update item quantities
- Track order status
- Mark orders as started (cooking)
- Complete orders
- Delete orders
- Support for multiple order sources (Swiggy, Zomato, Direct)

### 2. **Menu Management**
- Create/edit/delete categories
- Add/edit/delete menu items
- Price management
- Food type classification (veg/non-veg)
- Active/inactive toggle

### 3. **Table Management**
- Create and manage dining tables
- Track table occupancy status
- Link orders to specific tables

### 4. **Inventory Management**
- Track inventory items with quantities
- Multiple unit types (kg, g, l, ml, pcs, pkg, box)
- Automatic status tracking (in stock, low stock, out of stock)
- Reorder level configuration
- Transaction history (purchase, usage, adjustment, writeoff)
- Inventory valuation

### 5. **Financial Management**
- Order-based billing
- Payment processing (Cashfree integration)
- UPI payment support
- Discount management
- Payment record tracking
- Financial reports and analytics

### 6. **Reporting & Analytics**
- Sales reports (daily, monthly, custom period)
- Revenue tracking
- Time-based analysis (peak hours)
- User activity tracking
- Inventory reports
- Financial summaries

### 7. **Staff Management**
- Add/edit/delete staff members
- Role-based access control
- Staff assignment to restaurants
- Staff performance tracking

### 8. **System Administration**
- Database backup and restore
- Database optimization
- Git repository management
- User activity logs
- System monitoring

### 9. **Multi-Restaurant Support**
- Single platform for multiple restaurants
- Agent-based restaurant management
- Separate data isolation per restaurant

### 10. **Billing & Subscriptions**
- Subscription plans
- Payment gateway integration (Cashfree)
- Webhook handling for payment confirmation
- Billing history
- Plan expiry management

---

## Authentication & Security

- **Custom User Model:** Extended Django User with role field
- **Role-Based Access Control:** View-level and model-level permissions
- **Decorator-Based Protection:** `@login_required` for protected views
- **Automatic Redirection:** Post-login routing based on user role
- **CSRF Protection:** Django CSRF middleware
- **Payment Verification:** Signature verification for payment webhooks

---

## API Integrations

### 1. **Twilio**
- SMS notifications
- Phone number verification
- Message delivery

### 2. **Cashfree**
- Payment gateway integration
- Payment link generation
- Webhook-based payment confirmation
- Signature verification for security

### 3. **Django Admin**
- Built-in admin interface
- User and model management
- Database browsing

---

## File Structure Summary

```
restrauntapp/
├── app/ ────────────────── Core restaurant models & views
├── owner/ ──────────────── Owner dashboard & management
├── staff/ ──────────────── Staff interface
├── superadmin/ ─────────── Admin operations
├── authn/ ──────────────── Authentication
├── frontsite/ ──────────── Public website
├── agent/ ──────────────── Agent management
├── userApp/ ────────────── Customer app
├── templates/ ──────────── HTML templates
├── static/ ─────────────── CSS, JS, images
├── staticfiles/ ────────── Collected static files
├── restrauntapp/ ───────── Django settings & configuration
├── db.sqlite3 ──────────── SQLite database
├── manage.py ───────────── Django management script
├── requirements.txt ────── Python dependencies
└── DOCUMENTATION/ ──────── Documentation files
```

---

## Deployment Information

- **Hosting Platform:** PythonAnywhere
- **Live URL:** https://hotelsoftware.pythonanywhere.com/
- **Mobile App:** Android APK (25 MB) - Available for download
- **Database:** SQLite (local), AWS RDS MySQL (production-ready configuration available)

---

## Contact & Access

- **Web Application:** https://hotelsoftware.pythonanywhere.com/
- **Mobile APK:** https://median.co/share/zjembl#apk
- **Documentation Updated:** January 17, 2026
