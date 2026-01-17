# Module Documentation - Detailed Breakdown

## 1. APP MODULE (Core)

### Purpose
Core restaurant operations module containing main data models and basic views.

### Models

#### User
Custom Django user model extending AbstractUser
```
Fields:
- hint (CharField) - Security hint for password recovery
- phone (CharField) - User contact number
- city (CharField) - User location
- role (CharField) - User role (superadmin, admin, agent, owner, staff)
- staffof (ForeignKey) - Link to hotel if staff member

Roles:
- superadmin: System administrator with full access
- admin: Administrative privileges (unused in current implementation)
- agent: Restaurant agent/partner manager
- owner: Restaurant owner/manager
- staff: Kitchen or serving staff
```

#### Hotel
Restaurant/Hotel entity
```
Fields:
- name (CharField) - Restaurant name (unique)
- address (TextField) - Restaurant location
- owner (ForeignKey: User) - Restaurant owner
- status (Boolean) - Active/Inactive status
- agent (ForeignKey: User) - Assigned agent (nullable)
- expiry (DateField) - Subscription expiry date (default: 10 days from creation)

Purpose: Represents a single restaurant in the system
Multi-tenant: Each restaurant has isolated data
```

#### Table
Dining tables in restaurant
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- name (CharField) - Table name/number
- occupied (Boolean) - Current occupancy status

Purpose: Track physical tables in restaurant
Usage: Link orders to specific tables
```

#### MenuCategory
Categories for menu items
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- name (CharField) - Category name (Appetizers, Main Course, Desserts, etc.)
- icon (CharField) - Icon identifier for UI

Purpose: Organize menu items by type
```

#### MenuItem
Individual menu items/dishes
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- category (ForeignKey: MenuCategory) - Item category
- name (CharField) - Dish name
- price (DecimalField) - Item price
- active (Boolean) - Available/unavailable toggle
- food_type (CharField) - Veg/Non-veg classification

Purpose: Define restaurant's menu offerings
```

#### Order
Customer orders
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- table (ForeignKey: Table) - Table number (nullable for online orders)
- created_at (DateTimeField) - Order timestamp
- total (DecimalField) - Order total amount
- discount (DecimalField) - Discount applied
- completed (Boolean) - Order completion status
- started (Boolean) - Kitchen started preparing (cooking status)
- phone_number (CharField) - Customer contact
- completedby (ForeignKey: User) - Staff who completed order
- order_type (CharField) - 'table' or 'online'
- online_source (CharField) - Source if online (swiggy, zomato, free, other)

Purpose: Track customer orders
Workflow: Created → Started (cooking) → Completed (served)
```

#### OrderItems
Items in an order (many-to-many through table)
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- item (ForeignKey: MenuItem) - Menu item ordered
- order (ForeignKey: Order) - Parent order
- quantity (IntegerField) - Quantity ordered

Purpose: Track individual items in each order
Example: Order #5 contains 2x Biryani, 1x Raita, 3x Mango Lassi
```

#### PaymentDetails
Stored payment methods
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- upiid (CharField) - UPI ID (e.g., merchant@bank)
- name (CharField) - Account holder name

Purpose: Store restaurant's payment collection methods
```

#### InventoryItem
Stock/inventory items
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- name (CharField) - Item name (Rice, Oil, Tomato, etc.)
- description (TextField) - Item details
- quantity (DecimalField) - Current stock quantity
- unit (CharField) - Unit type (kg, g, l, ml, pcs, pkg, box)
- unit_price (DecimalField) - Price per unit
- reorder_level (DecimalField) - Low stock threshold (default: 10)
- status (CharField) - Auto-calculated (in_stock, low_stock, out_of_stock)
- category (ForeignKey: MenuCategory) - Item category
- last_updated (DateTimeField) - Last modification time
- created_at (DateTimeField) - Creation time

Auto-Calculation Logic:
- if quantity <= 0: out_of_stock
- elif quantity < reorder_level: low_stock
- else: in_stock

Purpose: Track raw materials and supplies
```

#### InventoryTransaction
Stock movement records
```
Fields:
- hotel (ForeignKey: Hotel) - Associated restaurant
- item (ForeignKey: InventoryItem) - Item affected
- transaction_type (CharField) - Type (purchase, usage, adjustment, writeoff)
- quantity (DecimalField) - Amount changed
- transaction_date (DateTimeField) - When it occurred
- notes (TextField) - Additional details
- created_by (ForeignKey: User) - Who performed transaction
- unit_price (DecimalField) - Price per unit (nullable)

Transaction Types:
- purchase: Incoming stock
- usage: Used in cooking
- adjustment: Manual correction
- writeoff: Damaged/expired items

Purpose: Audit trail for inventory changes
```

#### PaymentRecord
Payment transaction logs
```
Fields:
- user (ForeignKey: User) - Payer
- hotel (ForeignKey: Hotel) - Associated restaurant
- order_id (CharField) - Unique order reference
- amount (DecimalField) - Transaction amount
- status (CharField) - Payment status (PENDING, SUCCESS, FAILED)
- payment_link (CharField) - Payment gateway link
- created_at (DateTimeField) - Transaction timestamp

Purpose: Track all payment attempts and completions
Integration: Cashfree payment gateway
```

### Views
Mostly commented out in current implementation - features migrated to owner module

---

## 2. OWNER MODULE

### Purpose
Complete dashboard and management interface for restaurant owners

### Key Views & Features

#### Dashboard & Order Management

**owner()** - Main dashboard
- Shows all active orders
- Real-time order status
- New order creation form
- Quick action buttons

**submit_order(POST)**
```
Input: table_id, items (JSON)
Process:
1. Create Order instance
2. Loop through items and create OrderItems
3. Calculate total
4. Apply discount if applicable
5. Return response
Output: Order ID, total amount
```

**complete_order(POST)**
```
Input: order_id
Process:
1. Mark order.completed = True
2. Record user who completed it
3. Update table occupancy
Output: Success message
```

**delete_order(POST)**
```
Input: order_id
Process:
1. Delete associated OrderItems
2. Delete Order
3. Free up table
Output: Confirmation
```

**update_quantity(POST)**
```
Input: orderitem_id, new_quantity
Process:
1. Update OrderItems.quantity
2. Recalculate Order.total
3. Update UI
Output: New total
```

**set_order_started(POST)**
```
Input: order_id
Process:
1. Mark order.started = True
2. Signal to kitchen
Output: Status update
```

**ajax_get_orders(GET)**
- AJAX endpoint for real-time order updates
- Returns JSON with active orders
- Used by dashboard JavaScript

#### Menu Management

**add_category(POST)**
```
Fields: name, icon
Creates: MenuCategory for owner's hotel
```

**edit_category(POST)**
```
Input: category_id, name, icon
Updates: MenuCategory details
```

**delete_category(DELETE)**
```
Input: category_id
Process: Delete MenuCategory
Cascade: Delete associated MenuItems
```

**add_menu_item(POST)**
```
Fields: category_id, name, price, food_type, active
Creates: MenuItem
```

**edit_menu_item(POST)**
```
Input: item_id, price, active status, etc.
Updates: MenuItem
```

**delete_menu_item(DELETE)**
```
Input: item_id
Deletes: MenuItem
```

#### Table Management

**add_table(POST)**
```
Fields: table_name
Creates: Table
```

**edit_table(POST)**
```
Input: table_id, name
Updates: Table details
```

**delete_table(DELETE)**
```
Input: table_id
Deletes: Table
```

#### Reporting & Analytics

**sales()** - Sales overview
- Total sales
- Order count
- Average order value

**dailytransc()** - Daily transactions
```
Shows: Date-wise breakdown
Includes: Order count, total, discounts
Period: Configurable timeframe
```

**monthly_report()** - Monthly revenue
```
Calculates: Revenue by month
Displays: Trends, growth percentages
Includes: Top selling items
```

**revenue()** - Revenue tracking
- Cumulative revenue
- Period selection
- Export options

**timeanalysis()** - Peak hours analysis
```
Analyzes: Order distribution by time
Identifies: Busy hours
Helps: Staff scheduling
```

**custom_period(POST)**
```
Input: start_date, end_date
Returns: Sales data for custom date range
```

**reports()** - Report dashboard
- Navigation to all reports
- Report generation options

#### Staff Management

**staff()** - Staff list
- All staff members
- Roles and assignments
- Status

**add_staff(POST)**
```
Fields: username, password, phone, role, etc.
Creates: User with staff role
Assigns: To current hotel
```

**edit_staff(POST)**
```
Input: user_id, phone, role, etc.
Updates: User profile
```

**delete_staff(DELETE)**
```
Input: user_id
Removes: User from system
```

#### Inventory Management (in inventory_views.py)

**inventory()** - Inventory dashboard
```
Features:
- Filter by status (in_stock, low_stock, out_of_stock)
- Filter by category
- Search functionality
- Sort options (name, quantity, price, updated)
- Pagination (20 items per page)
- Metrics dashboard (total items, low stock count, out of stock count, inventory value)
```

**add_inventory_item(POST)**
```
Fields: name, description, quantity, unit, unit_price, reorder_level, category
Creates: InventoryItem
Auto-updates: Status based on quantity
```

**edit_inventory_item(POST)**
```
Input: item_id, quantity, unit_price, reorder_level, etc.
Updates: InventoryItem
Auto-updates: Status
```

**delete_inventory_item(DELETE)**
```
Input: item_id
Deletes: InventoryItem and its transactions
```

**add_transaction(POST)**
```
Input: item_id, transaction_type, quantity, notes, unit_price
Creates: InventoryTransaction record
Updates: InventoryItem.quantity based on transaction type
```

**view_transactions()** - Transaction history
```
Shows: All transactions for items
Includes: Purchase, usage, adjustment, writeoff
Sorted: Newest first
```

#### Billing & Payments

**payment()** - Payment management
- Payment method configuration
- UPI ID setup
- Payment status

**owner_billing()** - Billing overview
- Subscription status
- Renewal dates
- Payment history

**afterpay()** - Subscription management
- Available plans
- Current plan
- Renewal options

**get_payment(plan_id)** - Payment gateway
```
Process:
1. Get selected plan
2. Generate Cashfree payment link
3. Create PaymentRecord (PENDING)
4. Redirect to payment gateway
```

**verify_signature(payload, header_signature, secret_key)**
```
Purpose: Verify Cashfree webhook authenticity
Uses: HMAC signature verification
Returns: Boolean (valid/invalid)
```

**cashfree_webhook(POST)** - Payment webhook handler
```
Input: Cashfree webhook payload
Process:
1. Verify signature
2. Update PaymentRecord status
3. Update Hotel.expiry if payment successful
4. Log transaction
Output: Webhook response (200 OK)
```

**bill_history()** - Payment history
- All payment transactions
- Status and dates
- Amounts

**hotel_profile()** - Profile settings
- Restaurant name, address
- Contact information
- Settings

### Billing Plans Integration
- Plans defined in superadmin.models.BillingPlans
- Monthly/annual subscription options
- Automatic expiry date calculation
- Renewal reminders

---

## 3. STAFF MODULE

### Purpose
Interface for restaurant staff (waiters, servers)

### Views

**home()** - Staff dashboard
```
Purpose: Main staff view
Shows: Quick action buttons
Access: Staff members only (role='staff')
```

**waiter_active_orders()**
```
Purpose: Display active orders for serving
Shows:
- Table number
- Items
- Order status
- Preparation status (started/not started)
Filter: Only active orders (not completed)
Actions: 
- Serve order
- Check order status
```

### Features
- Real-time order viewing
- Order status tracking
- Table-based order filtering
- No order creation/modification (readonly access)

---

## 4. SUPERADMIN MODULE

### Purpose
Platform-wide administration and system management

### Models

**BillingPlans**
```
Fields:
- name (CharField, unique) - Plan name
- price (IntegerField) - Monthly/annual price
- active (Boolean) - Active/inactive
- description (TextField) - Plan features
- expiry_days (IntegerField) - Subscription duration (default: 30)

Purpose: Define subscription tiers
```

### Views & Features

#### User Management

**home()** - Admin dashboard
```
Shows:
- System statistics
- Active hotels
- Recent orders
- User count
- System health
```

**addagent(POST)**
```
Input: Username, password, phone, city
Creates: User with role='agent'
Output: Agent created, credentials
```

**users()** - User list
```
Shows: All users with roles
Features: 
- Pagination
- Filter by role
- Search by username
- Action buttons
```

**delete_user(user_id)**
```
Process:
1. Delete user and all related data
2. Delete associated hotels
3. Cleanup orders, staff assignments
Output: Confirmation
```

**view_user(user_id)**
```
Shows: User profile details
Includes:
- Role
- Contact info
- Associated hotels (if owner)
- Creation date
```

**edit_user(user_id, POST)**
```
Fields: username, email, phone, role, city, active status
Updates: User profile
```

**toggle_user_status(user_id)**
```
Process: Toggle is_active field
Effect: Disables/enables user account
Purpose: Suspend without deleting
```

#### Restaurant Management

**view_restaurant(hotel_id)**
```
Shows: Hotel profile
Includes:
- Owner information
- Restaurant details
- Menu info
- Staff count
- Active orders
- Revenue summary
```

**toggle_hotel_status(hotel_id)**
```
Process: Toggle hotel.status
Effect: Enable/disable restaurant operations
```

#### System Operations

**system_operations()**
```
Dashboard with:
- Server status monitoring
- Database stats
- User activity
- System health checks
- Recent logs
```

**git_pull()** - Repository management
```
Purpose: Update code from Git
Process: Execute git pull command
Usage: Hotfix deployments
```

#### Database Management

**database_management()** - DB admin panel
```
Features:
- Backup list with timestamps
- Restore options
- Optimization tools
- Database statistics
- Backup download/delete
```

**create_backup(POST)**
```
Process:
1. Dump database (sqlite3 or SQL)
2. Export to JSON format
3. Compress backup file
4. Store in backups/ folder
5. Record in database
Output: Backup file, metadata
```

**restore_backup(backup_id)**
```
Process:
1. Verify backup integrity
2. Create pre-restore backup
3. Load JSON data
4. Restore database state
5. Verify restoration
Output: Confirmation or error details
```

**delete_backup(backup_id)**
```
Purpose: Remove old backup files
Process: Delete file and database record
```

**optimize_database()**
```
Operations:
- VACUUM (SQLite)
- ANALYZE (SQLite)
- Remove orphaned records
- Cleanup temporary data
Output: Optimization report
```

**convert_sql_backups_to_json(backup_dir)**
```
Purpose: Convert SQL dumps to JSON format
Input: Backup directory path
Process:
1. Read SQL files
2. Parse data
3. Convert to JSON
4. Save as backup_name.json
Output: Converted files
```

#### Analytics & Reporting

**analytics_dashboard()** - System-wide analytics
```
Shows:
- Total revenue
- Order count
- User count
- Hotel count
- Growth metrics
- Charts and graphs
Time periods: Daily, monthly, custom
```

**financial_reports()** - Financial metrics
```
Shows:
- Revenue by restaurant
- Revenue by time period
- Top performing restaurants
- Payment breakdown
- Subscription revenue
- Outstanding payments
```

**user_activity()** - Activity tracking
```
Shows:
- Login history
- Active users
- User actions log
- Peak usage times
- Geographic distribution
```

**logs()** - System logs
```
Shows:
- Administrative actions
- Errors and warnings
- Database operations
- Payment transactions
- Backup operations
```

#### Billing Management

**adminplans()** - Billing plans
```
Shows: All subscription plans
Actions:
- Create new plan
- Edit plan
- Toggle active status
- View plan details
```

**delete_plan(plan_id)**
```
Process: Remove billing plan
Warning: Check for active subscriptions
```

---

## 5. AUTHN MODULE (Authentication)

### Purpose
User authentication and role-based routing

### Views

**owner_login(GET/POST)** - Login page
```
Input (POST): username, password
Process:
1. Authenticate user
2. Create session
3. Redirect based on role
Output: Session cookie
```

**logout_user(GET)**
```
Process:
1. Destroy session
2. Clear cookies
3. Redirect to login
Output: Logout page
```

**redirection()** - Post-login router
```
Automatic routing:
- superadmin → admin home
- owner → owner dashboard (or register hotel if first time)
- staff → staff home
- agent → agent home
- other → login page
```

**owner_register(GET/POST)** - Owner registration
```
Input: Username, email, password, phone, city, hint
Process:
1. Validate input
2. Create User with role='owner'
3. Set credentials
4. Auto-login
5. Redirect to hotel registration
```

**hotel_register(GET/POST)** - Restaurant registration
```
Input: Restaurant name, address
Process:
1. Create Hotel instance
2. Link to logged-in owner
3. Create default tables
4. Create default categories
5. Redirect to dashboard
```

---

## 6. FRONTSITE MODULE

### Purpose
Public-facing customer interface

### Views

**homepage(GET)** - Public homepage
```
Shows:
- Popular menu items (random 6)
- Menu categories
- Active restaurant info
- Restaurant highlights
Purpose: Customer-facing marketing page
```

---

## 7. AGENT MODULE

### Purpose
Partner agent management interface

### Views

**agenthome(GET)** - Agent dashboard
```
Access: Role='agent' only
Shows:
- Assigned restaurants
- Total sales from all restaurants
- Performance metrics
- Restaurant details
```

**demo(GET)** - Demo page
```
Purpose: Test/demo features
Shows: Sample data and interface
```

---

## 8. USERAPP MODULE

### Purpose
Mobile app menu interface for customers

### Views

**show_menu(GET)**
```
Parameters:
- hotel (required): Hotel/restaurant ID
- table (optional): Table ID (for dine-in)

Process:
1. Fetch hotel details
2. Get all categories for that hotel
3. Get all items in each category
4. Format for mobile display
5. Prefetch related items for performance

Output: Menu page with:
- Categories as tabs/sections
- Items with prices
- Item details
- Add to cart functionality
- Table info (if dine-in)
```

---

## 9. PAYMENT INTEGRATION (Cashfree)

### Workflow

```
Customer → Browser → Django → Cashfree Gateway → Payment
                       ↓
                    Webhook ← Cashfree (Payment Result)
                       ↓
                  Verify Signature
                       ↓
                  Update PaymentRecord
                       ↓
                  Update Hotel Expiry
                       ↓
                  Log Transaction
```

### Payment Flow

1. **Initiate Payment:**
   - Owner selects billing plan
   - System creates PaymentRecord (PENDING)
   - Generate Cashfree payment link
   - Redirect to Cashfree

2. **Payment Processing:**
   - Customer completes payment
   - Cashfree processes transaction

3. **Webhook Notification:**
   - Cashfree sends webhook to `cashfree_webhook()`
   - Signature verification using HMAC
   - Status update to PaymentRecord
   - Hotel expiry date extended

4. **Confirmation:**
   - Return 200 OK to Cashfree
   - Send confirmation email
   - Update owner dashboard

---

## 10. FORMS INTEGRATION

### Location: app/forms.py

Common form types:
- Order creation form
- Menu item form
- Category form
- Table form
- Staff user form
- Payment form
- Inventory forms

---

## Multi-Tenancy Architecture

### Data Isolation
- Every model with `hotel` ForeignKey ensures data belongs to specific restaurant
- Staff can only access their assigned hotel
- Agents can only access assigned restaurants
- SuperAdmin has full access

### Query Filtering
```python
# In views, typically filter by:
hotel = request.user.staffof  # For staff
hotel = request.user.hotel_set  # For owners (reverse relation)
```

### Security
- No cross-restaurant data leakage
- Role-based access control at view level
- URL-based hotel ID validation

---

## Performance Optimizations

### Database
- `select_related()`: Single queries for foreign keys
- `prefetch_related()`: Optimized reverse relations
- Pagination: 20 items per page in inventory
- Indexing on frequently queried fields

### Frontend
- AJAX for dynamic updates (no full page reload)
- Pagination for large lists
- Caching of categories and menu items

### Caching Opportunities
- Menu categories (change rarely)
- Billing plans
- Hotel information
- Staff lists

---

## Testing & Quality

### Key Test Areas
- Authentication and authorization
- Order management workflows
- Payment processing
- Multi-restaurant isolation
- Inventory calculations
- Backup/restore functionality
- Role-based access control

### Debug Tools
- Django debug toolbar (development)
- Admin interface
- Database query inspection
- Server logs
- Payment webhook testing

