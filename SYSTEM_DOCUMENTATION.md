# Inventory Management System - Complete Documentation

AI-Powered Inventory Management System with ML-based demand forecasting, customer management, batch tracking, and organization-based multi-tenancy.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Core Features](#core-features)
3. [Multi-Tenancy & Organizations](#multi-tenancy--organizations)
4. [Activity Feed](#activity-feed)
5. [API Reference](#api-reference)
6. [Security & Access Control](#security--access-control)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- SQLite (included)

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd inventory

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Initialize database
python scripts/init_sqlite.py
python scripts/add_activity_logs_table.py
python scripts/add_org_to_competitors.py

# 4. Seed data
python scripts/seed_activities.py

# 5. Start backend
python run_sqlite.py

# 6. Install frontend (new terminal)
cd frontend
npm install
npm start

# 7. Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:5000/api
```

### Default Login
- **Admin**: username: `admin`, password: `password123`
- **Manager**: username: `manager`, password: `password123`
- **Viewer**: username: `viewer`, password: `password123`

---

## Core Features

### Inventory Management
- Real-time stock tracking
- Automatic low-stock alerts
- Multi-location warehouse support
- Stock adjustment with reason tracking
- FIFO/LIFO batch valuation

### Product Management
- Full CRUD operations
- Category management
- Supplier linkage
- Reorder point configuration
- Safety stock levels

### Sales & POS
- Point-of-sale system
- Cart management
- Stock validation
- Customer-specific pricing
- Loyalty points integration

### Customer Management
- Customer types (Regular, VIP, Wholesale)
- Loyalty points system
- Special pricing per customer
- Credit limit tracking
- Purchase history

### Supplier Management
- Supplier database
- Lead time tracking
- Rating system
- Email/SMS contact
- Communication history

### Demand Forecasting
- ML-based predictions (Random Forest, Gradient Boosting, Linear Regression)
- 12-month historical analysis
- Accuracy metrics (MAE, RMSE, R²)
- Visual prediction charts

### Competitor Intelligence
- Category-based filtering
- Sales tracking
- Price comparison
- Market analysis

---

## Multi-Tenancy & Organizations

### Overview
Industry-standard multi-tenancy where users belong to organizations. All users in the same organization share data, while different organizations are completely isolated.

### Organization Model
- Users belong to one organization
- All data (products, customers, suppliers, etc.) is organization-specific
- Complete data isolation between organizations
- Role-based permissions within organizations

### User Roles
1. **Admin**
   - Full access to everything
   - Manage users and organization settings
   - Invite new members
   - Change member roles

2. **Manager**
   - Edit products, inventory, sales, customers
   - View all data
   - Cannot manage users or organization

3. **Viewer**
   - Read-only access
   - Cannot edit or delete anything
   - Cannot access admin features

### Registration Flow

**Option 1: Self-Registration (Creates New Organization)**
```
User registers → New organization created → User becomes admin
```

**Option 2: Invitation (Joins Existing Organization)**
```
Admin sends invite → User receives email → User accepts → User joins organization with assigned role
```

### Team Invitation System

**Sending Invitations (Admin Only)**
1. Navigate to Organization page
2. Click "Invitations" tab
3. Click "Invite User"
4. Enter email and select role
5. User receives invitation email with 48-hour expiry

**Accepting Invitations**
1. Click link in invitation email
2. Create account with username and password
3. Automatically join organization with assigned role

**Managing Invitations**
- View all pending/accepted/expired invitations
- Resend expired invitations
- Revoke pending invitations

### Organization Management

**Settings Tab (Admin Only)**
- Edit organization name
- View creation date
- View member count

**Members Tab (Admin/Manager)**
- View all organization members
- Change member roles (Admin only)
- Remove members (Admin only)
- Cannot modify own role or remove self
- Cannot remove other admins

**Invitations Tab (Admin Only)**
- View all invitations
- Resend invitations
- Revoke pending invitations

---

## Activity Feed

### Overview
Comprehensive activity logging system that tracks all user actions within organizations. Provides transparency, audit trails, and team awareness.

### Features
- **Automatic Logging**: All major operations logged automatically
- **Organization Isolation**: Only see activities from your organization
- **Real-time Updates**: Auto-refreshes every 30 seconds
- **Date Grouping**: Activities grouped by Today, Yesterday, specific dates
- **Filtering**: Filter by resource type and user
- **Relative Timestamps**: Human-readable time ("2 minutes ago")

### Logged Activities

**Products**
- Created product
- Updated product
- Deleted product

**Customers**
- Created customer
- Updated customer

**Suppliers**
- Created supplier
- Updated supplier

**Inventory**
- Adjusted stock for inventory

**Invitations**
- Sent invitation to user
- Accepted invitation and joined organization

**Organization Management**
- Updated organization settings
- Changed role to [role] for member
- Removed member

### Access
- **Dashboard Widget**: Shows last 20 activities with "View All" button
- **Activity Page**: Full page showing last 50 activities with filters
- **Access Control**: Manager and Admin only (Viewers redirected)

### API Endpoint
```
GET /api/activity?limit=50
Authorization: Bearer <token>

Response:
[
  {
    "id": 1,
    "username": "admin",
    "action": "created",
    "resource_type": "product",
    "resource_name": "Coca Cola 500ml",
    "description": "admin created product Coca Cola 500ml",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

---

## API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication
All endpoints (except login/register) require JWT token:
```
Authorization: Bearer <access_token>
```

### Key Endpoints

**Authentication**
```
POST /auth/login
POST /auth/register
POST /auth/refresh
GET /auth/me
```

**Products**
```
GET /products
POST /products
PUT /products/:id
DELETE /products/:id
```

**Inventory**
```
GET /inventory/items
POST /inventory/items/:id/adjust
GET /inventory/low-stock
```

**Customers**
```
GET /customers
POST /customers
PUT /customers/:id
POST /customers/:id/loyalty
POST /customers/:id/special-price
```

**Suppliers**
```
GET /suppliers
POST /suppliers
PUT /suppliers/:id
POST /suppliers/:id/contact
```

**Sales**
```
GET /sales
GET /sales/analytics/daily
GET /sales/analytics/monthly
```

**Competitors**
```
GET /competitors
GET /competitors/:id
GET /competitors/:id/products
GET /competitors/:id/sales
```

**Users (Admin Only)**
```
GET /users
POST /users
PUT /users/:id
DELETE /users/:id
```

**Invitations (Admin Only)**
```
POST /invitations
GET /invitations
GET /invitations/validate?token=<token>
POST /invitations/accept
```

**Organizations**
```
GET /organizations/settings
PUT /organizations/settings (Admin)
GET /organizations/members
PUT /organizations/members/:id/role (Admin)
DELETE /organizations/members/:id (Admin)
GET /organizations/invitations (Admin)
DELETE /organizations/invitations/:id (Admin)
POST /organizations/invitations/:id/resend (Admin)
```

**Activity**
```
GET /activity?limit=50
```

---

## Security & Access Control

### Authentication
- JWT-based authentication
- Access token (24 hours)
- Refresh token (30 days)
- Password hashing with bcrypt

### Authorization
- Role-based access control (RBAC)
- Organization-based data isolation
- Route-level permission checks
- Frontend route guards

### Data Isolation
- All queries filter by organization_id from JWT
- Users can only access data from their organization
- Complete isolation between organizations
- No cross-organization data leakage

### Security Best Practices
- SQL injection protection via SQLAlchemy ORM
- CORS configuration
- Environment variable protection
- No credentials in code
- PII substitution in examples

---

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt

# Reinitialize database
python scripts/init_sqlite.py
```

### Frontend Errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Database Issues
```bash
# Reset database
rm instance/inventory.db
python scripts/init_sqlite.py
python scripts/add_activity_logs_table.py
python scripts/add_org_to_competitors.py
python scripts/seed_activities.py
```

### Missing Authorization Token
- Check that access_token exists in localStorage
- Verify token is included in request headers
- Token format: `Authorization: Bearer <token>`

### Organization Data Not Showing
- Verify organization_id is in JWT token
- Check backend logs for SQL queries
- Ensure migrations ran successfully
- Verify user belongs to organization

### Activity Feed Not Loading
```bash
# Run migration
python scripts/add_activity_logs_table.py

# Seed sample data
python scripts/seed_activities.py
```

### Competitors Not Showing
```bash
# Run migration
python scripts/add_org_to_competitors.py

# Verify you have products (competitors filter by category)
```

---

## Tech Stack

**Backend**
- Python 3.11
- Flask (REST API)
- SQLAlchemy (ORM)
- JWT Authentication
- Scikit-learn, TensorFlow (ML)

**Frontend**
- React 18
- Material-UI
- Axios
- Chart.js
- React Router

**Database**
- SQLite (Development)
- PostgreSQL (Production - optional)

---

## Project Structure

```
inventory/
├── app/                    # Backend application
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   ├── utils/             # Utilities
│   └── __init__.py        # App factory
├── frontend/              # React application
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── context/      # React context
│   └── package.json
├── ml/                    # Machine learning
│   ├── data_processing/  # Data preprocessing
│   ├── models/           # ML models
│   └── utils/            # ML utilities
├── scripts/               # Database scripts
│   ├── init_sqlite.py
│   ├── add_activity_logs_table.py
│   ├── add_org_to_competitors.py
│   └── seed_activities.py
├── instance/              # SQLite database
│   └── inventory.db
├── requirements.txt       # Python dependencies
├── run_sqlite.py         # Start backend
└── README.md             # This file
```

---

## Support

For issues or questions:
1. Check this documentation
2. Review backend logs
3. Check browser console
4. Verify database migrations ran successfully
5. Test API endpoints directly

---

## License

Proprietary - All rights reserved

---

Built with modern technologies for efficient inventory management and team collaboration.
