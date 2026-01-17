# User Roles & Permissions Documentation

## Role Hierarchy & Access Control

```
                          SYSTEM ACCESS PYRAMID
                                  │
                          ┌────────▼────────┐
                          │   SUPERADMIN    │ (Full Access)
                          └─────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
            ┌───────▼──────┐ ┌────▼─────┐ ┌────▼──────┐
            │    AGENT     │ │  OWNER   │ │   STAFF   │
            └──────────────┘ └──────────┘ └───────────┘
                    │             │             │
                    │             │             │
            ┌───────▼─────────────▼─────────────▼───────┐
            │          USER (CUSTOMER)                  │
            └───────────────────────────────────────────┘
```

---

## 1. SUPERADMIN (System Administrator)

### Access Level
**Full System Access** - Complete control over the entire platform

### Permissions

#### User Management
- ✓ View all users
- ✓ Create users (all roles)
- ✓ Edit user information
- ✓ Delete users
- ✓ Activate/deactivate user accounts
- ✓ Assign roles
- ✓ Filter and search users
- ✓ View user details and activity

#### Restaurant Management
- ✓ View all restaurants
- ✓ Access any restaurant's data
- ✓ Enable/disable restaurants
- ✓ View restaurant details and metrics
- ✓ Monitor restaurant performance
- ✓ Access all orders from all restaurants
- ✓ Override owner permissions

#### Order Management
- ✓ View orders from all restaurants
- ✓ Complete/delete orders
- ✓ Access full order history
- ✓ Modify order details

#### Financial Management
- ✓ View all payments
- ✓ View all subscriptions
- ✓ Manage billing plans
- ✓ Create new billing plans
- ✓ Edit billing plans
- ✓ Delete billing plans
- ✓ View financial reports
- ✓ Generate billing statements

#### Database Management
- ✓ Create database backups
- ✓ Restore from backups
- ✓ Delete backups
- ✓ Optimize database
- ✓ Convert backup formats
- ✓ View database statistics
- ✓ Database maintenance tasks

#### System Operations
- ✓ View system logs
- ✓ Monitor system health
- ✓ Execute Git pulls (code updates)
- ✓ View system operations
- ✓ Access monitoring dashboard
- ✓ View error logs

#### Analytics & Reporting
- ✓ Access system-wide analytics
- ✓ View financial reports
- ✓ View user activity logs
- ✓ Generate custom reports
- ✓ Access platform statistics
- ✓ Monitor platform growth
- ✓ View revenue analytics

### View Access
```
/ (redirects to superadmin home)
/superadmin/home/
/superadmin/users/
/superadmin/users/view/<user_id>/
/superadmin/users/edit/<user_id>/
/superadmin/users/delete/<user_id>/
/superadmin/users/toggle/<user_id>/
/superadmin/restaurants/
/superadmin/restaurants/<hotel_id>/
/superadmin/restaurants/toggle/<hotel_id>/
/superadmin/database/
/superadmin/database/backup/create/
/superadmin/database/backup/restore/<backup_id>/
/superadmin/database/backup/delete/<backup_id>/
/superadmin/database/optimize/
/superadmin/operations/
/superadmin/operations/git-pull/
/superadmin/analytics/
/superadmin/financial-reports/
/superadmin/user-activity/
/superadmin/logs/
/superadmin/plans/
/superadmin/plans/delete/<plan_id>/
```

### Dashboard
- System statistics
- User count
- Restaurant count
- Total revenue
- Active users
- Recent orders

---

## 2. AGENT (Partner/Manager)

### Access Level
**Assigned Restaurants Only** - Limited to restaurants under their management

### Permissions

#### Restaurant Management
- ✓ View assigned restaurants
- ✓ Access assigned restaurants' data only
- ✗ Cannot create/modify restaurant info
- ✓ View restaurant performance metrics
- ✓ View assigned restaurants' orders

#### Order Viewing
- ✓ View orders from assigned restaurants
- ✓ View order history
- ✓ View order details
- ✗ Cannot modify orders
- ✗ Cannot complete orders (no kitchen access)

#### Analytics & Reporting
- ✓ View analytics for assigned restaurants
- ✓ View sales reports for assigned restaurants
- ✓ View revenue from assigned restaurants
- ✓ View performance metrics
- ✗ Cannot access other agents' restaurants

### View Access
```
/redirection/ (routes to agent home)
/agent/
/agent/demo/ (optional demo interface)
```

### Dashboard
- Assigned restaurants list
- Total sales from all assigned restaurants
- Order count
- Performance metrics
- Restaurant details

### Restrictions
- Cannot access restaurants not assigned to them
- Cannot modify any data (read-only for orders)
- Cannot access SuperAdmin functions
- Cannot manage users
- Cannot access billing/payment info

---

## 3. OWNER (Restaurant Manager/Owner)

### Access Level
**Own Restaurant Only** - Full control over their restaurant's operations

### Permissions

#### Restaurant Management
- ✓ View own restaurant details
- ✓ Edit restaurant profile
- ✓ Update address and contact
- ✓ View restaurant status
- ✓ View expiry date
- ✗ Cannot delete restaurant (SuperAdmin only)
- ✗ Cannot view other restaurants

#### Menu Management
- ✓ Create menu categories
- ✓ Edit categories
- ✓ Delete categories
- ✓ Add menu items
- ✓ Edit menu items
- ✓ Delete menu items
- ✓ Set prices
- ✓ Toggle item availability
- ✓ Classify food type (veg/non-veg)
- ✗ Cannot access other restaurants' menus

#### Table Management
- ✓ Create tables
- ✓ Edit tables
- ✓ Delete tables
- ✓ View table status
- ✓ View table occupancy
- ✗ Cannot view other restaurants' tables

#### Order Management
- ✓ Create orders (table/online)
- ✓ View all orders
- ✓ Update order quantities
- ✓ Complete orders
- ✓ Delete orders
- ✓ Set order status (started/completed)
- ✓ Apply discounts
- ✓ View order history
- ✓ Search orders
- ✗ Cannot create orders for other restaurants

#### Payment Management
- ✓ Configure UPI payment details
- ✓ View payment history
- ✓ View payment status
- ✓ Generate payment links
- ✓ Access billing information
- ✓ Select billing plans
- ✓ Initiate payment for subscription
- ✓ View bill history

#### Inventory Management
- ✓ View inventory items
- ✓ Add inventory items
- ✓ Edit inventory items
- ✓ Delete inventory items
- ✓ Filter by status/category
- ✓ Search inventory
- ✓ Sort inventory
- ✓ View item details
- ✓ Record transactions (purchase, usage, adjustment, writeoff)
- ✓ View transaction history
- ✓ View inventory metrics
- ✓ Set reorder levels
- ✗ Cannot access other restaurants' inventory

#### Staff Management
- ✓ View staff list
- ✓ Add staff members
- ✓ Edit staff information
- ✓ Delete staff
- ✓ Assign to restaurant
- ✓ Set staff roles
- ✗ Cannot manage users outside their restaurant
- ✗ Cannot access SuperAdmin features

#### Reports & Analytics
- ✓ View sales reports
- ✓ View daily transactions
- ✓ View monthly reports
- ✓ View revenue tracking
- ✓ View peak hours analysis
- ✓ View custom period reports
- ✓ Access dashboard analytics
- ✓ View financial reports (own restaurant)
- ✗ Cannot view other restaurants' reports

### View Access
```
/redirection/ (routes to owner home)
/owner/
/owner/orders/
/owner/orders/submit/
/owner/orders/complete/
/owner/orders/delete/
/owner/orders/update-qty/
/owner/orders/start/
/owner/menu/
/owner/menu/category/add/
/owner/menu/category/edit/
/owner/menu/category/delete/
/owner/menu/item/add/
/owner/menu/item/edit/
/owner/menu/item/delete/
/owner/tables/
/owner/tables/add/
/owner/tables/edit/
/owner/tables/delete/
/owner/staff/
/owner/staff/add/
/owner/staff/edit/
/owner/staff/delete/
/owner/reports/
/owner/reports/daily/
/owner/reports/monthly/
/owner/reports/custom-period/
/owner/reports/revenue/
/owner/reports/time-analysis/
/owner/inventory/
/owner/inventory/add/
/owner/inventory/edit/
/owner/inventory/delete/
/owner/inventory/transactions/
/owner/inventory/transactions/add/
/owner/payments/
/owner/payments/history/
/owner/payments/link/
/owner/billing/
/owner/profile/
```

### Dashboard
- Active orders
- Menu overview
- Staff list
- Revenue summary
- Inventory status
- Subscription expiry
- Recent activity

### Restrictions
- Cannot access other restaurants' data
- Cannot access SuperAdmin functions
- Cannot view other restaurants' orders
- Cannot modify staff outside their restaurant
- Cannot access database management
- Cannot manage users globally
- Cannot view system logs or operations

---

## 4. STAFF (Waiter/Kitchen Staff)

### Access Level
**Assigned Restaurant Only** - View and assist with orders

### Permissions

#### Order Management (Limited)
- ✓ View active orders
- ✓ View order details
- ✓ View items in orders
- ✓ View table assignments
- ✓ View order status
- ✗ Cannot create orders
- ✗ Cannot modify orders
- ✗ Cannot complete orders (only owner can)
- ✗ Cannot delete orders
- ✗ Cannot access other restaurants' orders

#### Restaurant Access
- ✓ View assigned restaurant
- ✓ View tables
- ✓ View menu (for reference)
- ✗ Cannot modify restaurant info
- ✗ Cannot create/edit menu
- ✗ Cannot manage tables
- ✗ Cannot access other restaurants

#### Dashboard
- ✓ View active orders
- ✓ Check order status
- ✓ See table information
- ✓ View items to prepare

### View Access
```
/redirection/ (routes to staff home)
/staff/
/staff/orders/ (active orders only)
```

### Restrictions
- Cannot create/modify/delete orders
- Cannot access owner/admin functions
- Cannot access billing or payment
- Cannot view reports
- Cannot manage staff
- Cannot manage inventory
- Cannot access database
- Cannot access other restaurants' data
- Read-only access to orders
- Cannot complete orders
- Cannot access SuperAdmin features

---

## 5. USER / CUSTOMER

### Access Level
**Public Menu & Ordering** - Limited to menu browsing and order placement

### Permissions

#### Menu Access
- ✓ Browse restaurant menu
- ✓ View categories
- ✓ View menu items
- ✓ View prices
- ✓ View food type (veg/non-veg)
- ✗ Cannot modify menu
- ✗ Cannot access other sections

#### Order Placement
- ✓ View menu for restaurant
- ✓ Select items
- ✓ Add to cart
- ✓ Specify quantities
- ✓ Place order (implied)
- ✗ Cannot modify after placement (implied)
- ✗ Cannot access admin functions

#### Website Access
- ✓ Browse homepage
- ✓ View popular items
- ✓ View restaurant info
- ✓ Access public pages
- ✗ Cannot access admin areas

### View Access
```
/ (public homepage)
/site/homepage/
/user/getmenu/<hotel_id>/
/user/getmenu/<hotel_id>/<table_id>/
```

### Dashboard
- Menu display
- Order form (implied)
- Restaurant information
- Categories and items

### Restrictions
- Cannot access any admin functions
- Cannot create users
- Cannot manage restaurants
- Cannot view other customers' orders
- Cannot access billing/payment (for self)
- Cannot view staff areas
- Cannot access reports
- Cannot modify menu
- Cannot create accounts (registration by owner)
- Public access only to menu

---

## ACCESS CONTROL IMPLEMENTATION

### View-Level Access Control
```python
@login_required
def owner_view(request):
    # Only owner role can access
    if request.user.role != 'owner':
        return HttpResponse('Access Denied')
    hotel = request.user.staffof
    # Access only their restaurant's data
    orders = Order.objects.filter(hotel=hotel)
    return render(request, 'owner/dashboard.html', {...})
```

### URL-Level Access Control
```python
# URL parameter validation
hotel_id = request.GET.get('hotel')
if not Hotel.objects.filter(id=hotel_id, owner=request.user).exists():
    return HttpResponse('Access Denied')
```

### Model-Level Filtering
```python
# Always filter by owner's restaurant
items = MenuItem.objects.filter(hotel__owner=request.user)

# For staff
items = MenuItem.objects.filter(hotel=request.user.staffof)
```

---

## Permission Checking Decorator

The system uses decorators to enforce role-based access:
```python
@login_required
def protected_view(request):
    if request.user.role not in ['owner', 'superadmin']:
        return redirect('access_denied')
    # Continue with view logic
```

---

## Access Denial Handling

When a user attempts to access unauthorized content:
- Redirect to login if not authenticated
- Redirect to home if wrong role
- Show error message
- Log unauthorized access attempt (implied)

---

## Multi-Restaurant Data Isolation

Critical Features for Security:
1. **Every query filtered by restaurant**
   - Staff/Owner cannot see cross-restaurant data
   - Agent can only see assigned restaurants
   - SuperAdmin sees everything

2. **URL Validation**
   - Check if user has access to restaurant in URL
   - Prevent parameter manipulation

3. **View Decorators**
   - Enforce role requirements
   - Redirect on access denial

---

## Session & Authentication

- **Session Storage:** Django session framework
- **Session Duration:** Browser session (logout to end)
- **Token-Based:** (For API integration with mobile app)
- **CSRF Protection:** On all POST requests
- **Secure Cookies:** HTTPS in production

---

## Default Permissions by Role

```
SUPERADMIN: Allow All
  └─ Default deny for unimplemented features

AGENT: Allow (Own Restaurants)
  └─ Default deny for other restaurants

OWNER: Allow (Own Restaurant)
  └─ Default deny for other restaurants

STAFF: Allow (Read Orders)
  └─ Default deny for modifications

CUSTOMER: Allow (Public Menu)
  └─ Default deny for all protected areas
```

---

**Documentation Updated:** January 17, 2026
