# Database & API Documentation

## DATABASE SCHEMA

### Database Type
- **Development:** SQLite3 (db.sqlite3)
- **Production Ready:** MySQL/PostgreSQL (AWS RDS configuration available)

### Table Relationships Diagram

```
                    ┌──────────────┐
                    │    User      │
                    │  (Custom)    │
                    └────────┬─────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                │            │            │
         ┌──────▼──────┐     │    ┌───────▼─────────┐
         │   Hotel     │     │    │   StaffOf       │
         │ (Restaurant)│     │    │   (Foreign Key) │
         └──────┬──────┘     │    └─────────────────┘
                │            │
    ┌───────────┼────────────│
    │           │            │
    │     ┌─────▼────────────┘
    │     │ (owner)      (staff member)
    │     │
┌───▼─────▼────┐    ┌──────────────┐
│   Table      │    │PaymentDetails│
│ (Dining)     │    │  (UPI)       │
└───┬──────────┘    └──────────────┘
    │
    │          ┌──────────────────┐
    │          │  MenuCategory    │
    │          │  (By Hotel)      │
    │          └─────────┬────────┘
    │                    │
    │            ┌───────▼────────┐
    │            │    MenuItem    │
    │            │  (Menu Items)  │
    │            └────────┬───────┘
    │                     │
┌───▼─────────┐     ┌─────▼──────────┐
│   Order     │     │   OrderItems   │
│ (Customer)  │────▶│ (Order Details)│
└───┬─────────┘     └────────────────┘
    │
    │       ┌──────────────────┐
    │       │ PaymentRecord    │
    │       │  (Transactions)  │
    │       └──────────────────┘
    │
    │       ┌──────────────────┐
    │       │ InventoryItem    │ 
    │       │  (Stock)         │
    │       └───────┬──────────┘
    │               │
    │       ┌───────▼─────────────┐
    │       │ InventoryTransaction│
    │       │  (Stock Movement)   │
    │       └─────────────────────┘
    │
    └───────────────┘

    ┌──────────────────┐
    │  BillingPlans    │
    │ (Subscription)   │
    └──────────────────┘
```

### Core Tables & Fields

#### Users Table
```sql
CREATE TABLE app_user (
  id INTEGER PRIMARY KEY,
  username VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(254) UNIQUE,
  first_name VARCHAR(150),
  last_name VARCHAR(150),
  phone VARCHAR(15),
  city VARCHAR(100),
  hint VARCHAR(40),
  role VARCHAR(10) NOT NULL,
  staffof_id INTEGER FOREIGN KEY,
  is_active BOOLEAN DEFAULT TRUE,
  is_staff BOOLEAN DEFAULT FALSE,
  created_at DATETIME,
  modified_at DATETIME,
  
  FOREIGN KEY (staffof_id) REFERENCES app_hotel(id)
);
```

#### Hotels Table
```sql
CREATE TABLE app_hotel (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  address TEXT,
  owner_id INTEGER FOREIGN KEY NOT NULL,
  agent_id INTEGER FOREIGN KEY,
  status BOOLEAN DEFAULT FALSE,
  expiry DATE,
  created_at DATETIME,
  
  FOREIGN KEY (owner_id) REFERENCES app_user(id),
  FOREIGN KEY (agent_id) REFERENCES app_user(id)
);
```

#### Tables Table
```sql
CREATE TABLE app_table (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  occupied BOOLEAN DEFAULT FALSE,
  created_at DATETIME,
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id)
);
```

#### Menu Categories Table
```sql
CREATE TABLE app_menucategory (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  icon VARCHAR(50),
  created_at DATETIME,
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id)
);
```

#### Menu Items Table
```sql
CREATE TABLE app_menuitem (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  category_id INTEGER FOREIGN KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  price DECIMAL(6,2) NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  food_type VARCHAR(10),
  created_at DATETIME,
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id),
  FOREIGN KEY (category_id) REFERENCES app_menucategory(id)
);
```

#### Orders Table
```sql
CREATE TABLE app_order (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  table_id INTEGER FOREIGN KEY,
  created_at DATETIME NOT NULL,
  total DECIMAL(6,2) DEFAULT 0,
  discount DECIMAL(6,2) DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  started BOOLEAN DEFAULT FALSE,
  phone_number VARCHAR(15),
  completedby_id INTEGER FOREIGN KEY,
  order_type VARCHAR(10) DEFAULT 'table',
  online_source VARCHAR(10),
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id),
  FOREIGN KEY (table_id) REFERENCES app_table(id),
  FOREIGN KEY (completedby_id) REFERENCES app_user(id)
);
```

#### Order Items Table
```sql
CREATE TABLE app_orderitems (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  item_id INTEGER FOREIGN KEY NOT NULL,
  order_id INTEGER FOREIGN KEY NOT NULL,
  quantity INTEGER DEFAULT 1,
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id),
  FOREIGN KEY (item_id) REFERENCES app_menuitem(id),
  FOREIGN KEY (order_id) REFERENCES app_order(id)
);
```

#### Payment Details Table
```sql
CREATE TABLE app_paymentdetails (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  upiid VARCHAR(100) NOT NULL,
  name VARCHAR(100),
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id)
);
```

#### Inventory Items Table
```sql
CREATE TABLE app_inventoryitem (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  quantity DECIMAL(10,2),
  unit VARCHAR(3),
  unit_price DECIMAL(10,2),
  reorder_level DECIMAL(10,2),
  status VARCHAR(15),
  category_id INTEGER FOREIGN KEY,
  last_updated DATETIME,
  created_at DATETIME,
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id),
  FOREIGN KEY (category_id) REFERENCES app_menucategory(id)
);
```

#### Inventory Transactions Table
```sql
CREATE TABLE app_inventorytransaction (
  id INTEGER PRIMARY KEY,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  item_id INTEGER FOREIGN KEY NOT NULL,
  transaction_type VARCHAR(10) NOT NULL,
  quantity DECIMAL(10,2),
  transaction_date DATETIME,
  notes TEXT,
  created_by_id INTEGER FOREIGN KEY,
  unit_price DECIMAL(10,2),
  
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id),
  FOREIGN KEY (item_id) REFERENCES app_inventoryitem(id),
  FOREIGN KEY (created_by_id) REFERENCES app_user(id)
);
```

#### Payment Records Table
```sql
CREATE TABLE app_paymentrecord (
  id INTEGER PRIMARY KEY,
  user_id INTEGER FOREIGN KEY NOT NULL,
  hotel_id INTEGER FOREIGN KEY NOT NULL,
  order_id VARCHAR(100) UNIQUE NOT NULL,
  amount DECIMAL(10,2),
  status VARCHAR(20) DEFAULT 'PENDING',
  payment_link VARCHAR(200),
  created_at DATETIME,
  
  FOREIGN KEY (user_id) REFERENCES app_user(id),
  FOREIGN KEY (hotel_id) REFERENCES app_hotel(id)
);
```

#### Billing Plans Table
```sql
CREATE TABLE superadmin_billingplans (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  price INTEGER NOT NULL,
  active BOOLEAN DEFAULT TRUE,
  description TEXT,
  expiry_days INTEGER DEFAULT 30
);
```

---

## DATABASE INDEXES

Recommended indexes for performance:
```sql
CREATE INDEX idx_app_hotel_owner ON app_hotel(owner_id);
CREATE INDEX idx_app_hotel_agent ON app_hotel(agent_id);
CREATE INDEX idx_app_order_hotel ON app_order(hotel_id);
CREATE INDEX idx_app_order_table ON app_order(table_id);
CREATE INDEX idx_app_order_created ON app_order(created_at);
CREATE INDEX idx_app_menuitem_hotel ON app_menuitem(hotel_id);
CREATE INDEX idx_app_menuitem_category ON app_menuitem(category_id);
CREATE INDEX idx_app_inventoryitem_hotel ON app_inventoryitem(hotel_id);
CREATE INDEX idx_app_user_role ON app_user(role);
CREATE INDEX idx_app_paymentrecord_hotel ON app_paymentrecord(hotel_id);
```

---

## API ENDPOINTS

### Authentication Endpoints

#### Login
```
POST /auth/login/
Parameters:
  - username (required)
  - password (required)
Response:
  - 302 Redirect to dashboard (on success)
  - 200 Login page with error (on failure)
```

#### Logout
```
GET /auth/logout/
Response:
  - 302 Redirect to login
```

#### Redirection (Auto-router)
```
GET /redirection/
Response:
  - 302 Redirect to role-specific dashboard
```

### Registration Endpoints

#### Owner Registration
```
GET/POST /register/owner/
Input:
  - username
  - email
  - password
  - phone
  - city
  - hint
Response:
  - 302 Redirect to hotel registration (on success)
  - 200 Registration form (on GET or error)
```

#### Hotel Registration
```
GET/POST /register/hotel/
Input:
  - name
  - address
Response:
  - 302 Redirect to owner dashboard (on success)
  - 200 Registration form
```

### Order Management Endpoints

#### Submit Order
```
POST /owner/orders/submit/
Input:
  - table_id
  - items (JSON)
  - discount (optional)
Response:
  - {"success": true, "order_id": 123, "total": 450.50}
  - {"success": false, "error": "..."}
```

#### Complete Order
```
POST /owner/orders/complete/
Input:
  - order_id
Response:
  - {"success": true}
  - {"success": false, "error": "..."}
```

#### Delete Order
```
POST /owner/orders/delete/
Input:
  - order_id
Response:
  - {"success": true}
  - {"success": false}
```

#### Update Quantity
```
POST /owner/orders/update-qty/
Input:
  - orderitem_id
  - quantity
Response:
  - {"success": true, "new_total": 500.00}
  - {"success": false}
```

#### Set Order Started
```
POST /owner/orders/start/
Input:
  - order_id
Response:
  - {"success": true}
  - {"success": false}
```

#### Get Orders (AJAX)
```
GET /owner/orders/ajax-get/
Parameters:
  - hotel_id (optional)
Response:
  [
    {
      "id": 1,
      "table": "Table 1",
      "items": [...],
      "status": "started",
      "total": 450.50,
      "created_at": "2024-01-17 10:30:00"
    },
    ...
  ]
```

### Menu Management Endpoints

#### Add Category
```
POST /owner/menu/category/add/
Input:
  - name
  - icon
Response:
  - 302 Redirect to menu page
  - Message: Category added
```

#### Edit Category
```
POST /owner/menu/category/edit/
Input:
  - category_id
  - name
  - icon
Response:
  - 302 Redirect
  - Message: Category updated
```

#### Delete Category
```
POST /owner/menu/category/delete/<category_id>/
Response:
  - 302 Redirect
  - Message: Category deleted
```

#### Add Menu Item
```
POST /owner/menu/item/add/
Input:
  - category_id
  - name
  - price
  - food_type
  - active
Response:
  - 302 Redirect
  - Message: Item added
```

#### Edit Menu Item
```
POST /owner/menu/item/edit/
Input:
  - item_id
  - name
  - price
  - active
Response:
  - 302 Redirect
  - Message: Item updated
```

#### Delete Menu Item
```
POST /owner/menu/item/delete/<item_id>/
Response:
  - 302 Redirect
  - Message: Item deleted
```

### Inventory Endpoints

#### Get Inventory
```
GET /owner/inventory/
Parameters:
  - status (optional): in_stock, low_stock, out_of_stock
  - category (optional): category_id
  - search (optional): search string
  - sort (optional): name, quantity_asc, quantity_desc, price_asc, price_desc, updated
  - page (optional): page number
Response:
  - HTML page with inventory list
```

#### Add Inventory Item
```
POST /owner/inventory/add/
Input:
  - name
  - description
  - quantity
  - unit
  - unit_price
  - reorder_level
  - category_id
Response:
  - 302 Redirect
  - Message: Item added
```

#### Edit Inventory Item
```
POST /owner/inventory/edit/
Input:
  - item_id
  - quantity
  - unit_price
  - reorder_level
Response:
  - 302 Redirect
  - Message: Item updated
```

#### Add Transaction
```
POST /owner/inventory/transactions/add/
Input:
  - item_id
  - transaction_type (purchase, usage, adjustment, writeoff)
  - quantity
  - unit_price (optional)
  - notes
Response:
  - 302 Redirect
  - Message: Transaction recorded
```

### Reporting Endpoints

#### Daily Transactions
```
GET /owner/reports/daily/
Response:
  - HTML page with daily breakdown
```

#### Monthly Report
```
GET /owner/reports/monthly/
Response:
  - HTML page with monthly data
```

#### Custom Period Report
```
GET /owner/reports/custom-period/
Parameters:
  - start_date
  - end_date
Response:
  - HTML page with filtered data
```

#### Revenue Report
```
GET /owner/reports/revenue/
Response:
  - HTML page with revenue tracking
```

#### Time Analysis
```
GET /owner/reports/time-analysis/
Response:
  - HTML page with peak hours analysis
```

### Payment Endpoints

#### Get Payment Link
```
GET /owner/payments/link/<plan_id>/
Response:
  - Redirect to Cashfree payment page
  - Or error message
```

#### Payment Webhook
```
POST /owner/payments/webhook/
Headers:
  - X-Cashfree-Signature (HMAC)
Input:
  - Cashfree webhook JSON payload
Response:
  - {"status": "ok"}
  - {"error": "..."}
```

### Staff Endpoints

#### Add Staff
```
POST /owner/staff/add/
Input:
  - username
  - password
  - phone
  - role
Response:
  - 302 Redirect
  - Message: Staff added
```

#### Edit Staff
```
POST /owner/staff/edit/
Input:
  - user_id
  - phone
  - role
Response:
  - 302 Redirect
  - Message: Staff updated
```

#### Delete Staff
```
POST /owner/staff/delete/
Input:
  - user_id
Response:
  - 302 Redirect
  - Message: Staff deleted
```

### Public Menu Endpoint

#### Get Menu
```
GET /user/getmenu/<hotel_id>/
GET /user/getmenu/<hotel_id>/<table_id>/
Response:
  - HTML menu page
  - JSON menu data (optional)
```

---

## PAYMENT GATEWAY INTEGRATION

### Cashfree Integration

#### Configuration
```python
CASHFREE_APP_ID = "from_settings"
CASHFREE_SECRET_KEY = "from_settings"
CASHFREE_API_URL = "https://api.cashfree.com/pg/orders"
```

#### Payment Link Generation
```
POST https://api.cashfree.com/pg/orders
Headers:
  - X-Api-Version: 2023-08-01
  - X-Client-Id: {APP_ID}
  - X-Client-Secret: {SECRET_KEY}
Input:
  {
    "order_id": "unique_order_id",
    "order_amount": 100,
    "order_currency": "INR",
    "customer_details": {
      "customer_email": "customer@email.com",
      "customer_phone": "9876543210"
    },
    "order_meta": {
      "notify_url": "https://yourdomain.com/webhook",
      "return_url": "https://yourdomain.com/success"
    }
  }
Response:
  {
    "cf_order_id": 123456,
    "order_id": "order_12345",
    "order_status": "PENDING",
    "payment_link": "https://payments.cashfree.com/..."
  }
```

#### Webhook Signature Verification
```python
import hmac
import hashlib

def verify_signature(payload, header_signature, secret_key):
    computed_signature = hmac.new(
        secret_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return computed_signature == header_signature
```

### Twilio SMS Integration

#### Configuration
```python
TWILIO_ACCOUNT_SID = "from_settings"
TWILIO_AUTH_TOKEN = "from_settings"
TWILIO_PHONE_NUMBER = "from_settings"
```

#### Send SMS
```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
message = client.messages.create(
    body="Order #123 has been confirmed",
    from_=TWILIO_PHONE_NUMBER,
    to="+919876543210"
)
```

---

## DATA RELATIONSHIPS

### Multi-Tenancy
```
User (Owner) ──has──> Hotel
User (Staff) ──assigned_to──> Hotel (via staffof)
Hotel ──owns──> Table(s)
Hotel ──owns──> MenuCategory
Hotel ──owns──> MenuItem
Hotel ──owns──> Order(s)
Hotel ──owns──> InventoryItem(s)
Hotel ──owns──> PaymentDetails
```

### Order Cascade
```
Order
├── OrderItems[] (1:Many)
│   └── MenuItem (reference to menu item)
└── PaymentRecord[] (implied 1:Many)
```

### Inventory Audit
```
InventoryItem
└── InventoryTransaction[] (1:Many)
    ├── purchase
    ├── usage
    ├── adjustment
    └── writeoff
```

---

## QUERY OPTIMIZATION PATTERNS

### Select Related (Foreign Keys)
```python
# Optimized query for orders
orders = Order.objects.select_related('hotel', 'table', 'completedby')

# Optimized query for menu items
items = MenuItem.objects.select_related('hotel', 'category')
```

### Prefetch Related (Reverse Relations)
```python
# For categories with items
categories = MenuCategory.objects.prefetch_related('menuitem_set').filter(hotel=hotel)

# For orders with items
orders = Order.objects.prefetch_related('orderitems__item')
```

### Aggregation Queries
```python
# Total revenue
from django.db.models import Sum
total = Order.objects.filter(hotel=hotel).aggregate(Sum('total'))['total__sum']

# Count by status
from django.db.models import Count
status_counts = Order.objects.filter(hotel=hotel).values('started', 'completed').annotate(count=Count('id'))
```

---

**Documentation Updated:** January 17, 2026
