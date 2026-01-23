# Restaurant Management System

> Complete restaurant operations platform with web and mobile interfaces

## 📚 Complete Documentation

**👉 [View Full Documentation](DOCUMENTATION/README.md)** - Comprehensive guides for developers, admins, and managers

---

## 🌐 Live Application

- **Web App:** [https://hotelsoftware.pythonanywhere.com/](https://hotelsoftware.pythonanywhere.com/)
- **Homepage:** [https://hotelsoftware.pythonanywhere.com/homepage/](https://hotelsoftware.pythonanywhere.com/site/)

## 📱 Mobile App

- **Download APK:** [Restaurant App APK](https://median.co/share/zjembl#apk)
- **File Size:** ~25 MB
- **Min Android:** 6.0 (API 23)
- **Last Updated:** July 2025

## ✨ Key Features

- **Order Management** - Real-time order tracking and processing
- **Menu Management** - Dynamic menu with categories and pricing
- **Inventory System** - Stock tracking with transaction audit trail
- **Table Management** - Dining table organization and occupancy tracking
- **Billing & Payments** - Cashfree payment gateway + UPI integration
- **Staff Management** - Role-based access control (5 roles)
- **Analytics** - Sales, revenue, and peak hours reporting
- **Multi-tenancy** - Support for multiple restaurants on single platform
- **Mobile App** - Cross-platform Android application
- **Real-time Updates** - AJAX-based live order status
- **System Admin** - Database backups, user management, monitoring

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Django 5.2.6 (Python) |
| **Database** | SQLite (dev) / MySQL/PostgreSQL (prod) |
| **Frontend** | HTML, CSS, JavaScript |
| **Mobile** | Cordova (Android APK) |
| **Payments** | Cashfree API |
| **SMS** | Twilio API |
| **Hosting** | PythonAnywhere |

## 🚀 Quick Start

### For Web Application
No setup needed - visit [https://hotelsoftware.pythonanywhere.com/](https://hotelsoftware.pythonanywhere.com/)

### For Local Development
```bash
git clone <repo_url>
cd restrauntapp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Access: `http://localhost:8000/`

### For Mobile App
Download APK and install on Android 6.0+

---

## 📖 Documentation Structure

| Document | Purpose |
|----------|---------|
| [00_PROJECT_OVERVIEW](DOCUMENTATION/00_PROJECT_OVERVIEW.md) | Project scope & architecture |
| [01_MODULES_DETAILED](DOCUMENTATION/01_MODULES_DETAILED.md) | Code & module breakdown |
| [02_FEATURES_COMPLETE](DOCUMENTATION/02_FEATURES_COMPLETE.md) | All features documented |
| [03_ROLES_PERMISSIONS](DOCUMENTATION/03_ROLES_PERMISSIONS.md) | User roles & access control |
| [04_DATABASE_API](DOCUMENTATION/04_DATABASE_API.md) | Database schema & API endpoints |
| [05_INSTALLATION_DEPLOYMENT](DOCUMENTATION/05_INSTALLATION_DEPLOYMENT.md) | Setup & deployment guides |
| [06_FILE_STRUCTURE](DOCUMENTATION/06_FILE_STRUCTURE.md) | Project layout |
| [07_QUICK_REFERENCE](DOCUMENTATION/07_QUICK_REFERENCE.md) | Quick lookup tables |

**👉 [Full Documentation Index](DOCUMENTATION/README.md)**

---

## 👥 User Roles

- **SuperAdmin** - Full system control
- **Owner** - Restaurant management (orders, menu, staff, reports)
- **Agent** - Partner/distributor management
- **Staff** - Waiter/kitchen staff (view orders)
- **Customer** - Browse menu & place orders
