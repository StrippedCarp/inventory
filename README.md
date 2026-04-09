AI-Powered Inventory Management System

Complete inventory management system with ML-based demand forecasting, customer management, and batch tracking for SMEs.

========================================
QUICK START
========================================

Prerequisites
- Python 3.11+
- Node.js 16+
- SQLite (included) or PostgreSQL (optional)

Installation Steps

1. Clone repository
   git clone <repository-url>
   cd inventory-main

2. Install backend dependencies
   pip install -r requirements.txt

3. Initialize database
   python scripts/init_sqlite.py
   python scripts/seed_data.py
   python scripts/seed_customers_batches.py

4. Train ML models (optional)
   python ml/data_processing/preprocess_simple.py
   python ml/models/train_simple.py

5. Start backend
   python run_sqlite.py

6. Install frontend dependencies (new terminal)
   cd frontend
   npm install

7. Start frontend
   npm start

8. Access application
   Frontend: http://localhost:3000
   Backend API: http://localhost:5000/api

Default Login Credentials
- Admin: username: admin, password: password123
- Manager: username: manager, password: password123
- Viewer: username: viewer, password: password123

========================================
FEATURES
========================================

Core Features
- Inventory Management - Real-time stock tracking and adjustments
- Product Management - Full CRUD operations with auto-inventory creation
- POS System - Complete point-of-sale with cart and stock validation
- Demand Forecasting - ML-based predictions (Random Forest, Gradient Boosting, Linear Regression)
- Alert System - Automated low-stock notifications
- Supplier Management - Supplier database with contact functionality (Email/SMS)
- Analytics Dashboard - Sales performance and inventory insights
- User Management - Role-based access control (Admin/Manager/Viewer)

Advanced Features
- Customer Management - Customer database with loyalty points and special pricing
- Batch/Lot Tracking - Track products by batch with expiry dates and FIFO/LIFO valuation
- Competitor Intelligence - Track competitor sales and pricing
- Multi-Currency - All values in KES (Kenyan Shillings)

========================================
ARCHITECTURE
========================================

Multi-tier microservices architecture:
- Presentation Layer: React.js 18 with Material-UI
- Application Layer: Flask microservices (Inventory, Alerts, Forecasting, Customers, Batches)
- Data Layer: SQLite (dev) / PostgreSQL (prod)
- ML Layer: TensorFlow, Scikit-learn (Random Forest, Gradient Boosting, Linear Regression)

========================================
TECH STACK
========================================

Backend
- Python 3.11
- Flask (REST API)
- SQLAlchemy (ORM)
- JWT Authentication
- Scikit-learn, TensorFlow (ML)

Frontend
- React 18
- Material-UI
- Axios
- Chart.js
- React Router

Database
- SQLite (Development)
- PostgreSQL (Production - optional)

========================================
PROJECT STRUCTURE
========================================

inventory-main/
├── app/                          Backend application
│   ├── models/                   Database models
│   │   ├── batch.py             Batch tracking
│   │   ├── customer.py          Customer management
│   │   ├── competitor.py        Competitor intelligence
│   │   ├── product.py           Product catalog
│   │   ├── inventory.py         Stock management
│   │   ├── sales_transaction.py Sales records
│   │   ├── supplier.py          Supplier database
│   │   └── user.py              User authentication
│   ├── routes/                   API endpoints
│   │   ├── auth.py              Authentication
│   │   ├── products.py          Product CRUD
│   │   ├── inventory.py         Inventory operations
│   │   ├── sales.py             Sales transactions
│   │   ├── customers.py         Customer management
│   │   ├── batches.py           Batch tracking
│   │   ├── suppliers.py         Supplier operations
│   │   ├── competitors.py       Competitor data
│   │   ├── forecast.py          ML predictions
│   │   ├── alerts.py            Stock alerts
│   │   ├── analytics.py         Dashboard analytics
│   │   └── users.py             User management
│   ├── utils/                    Utilities
│   │   ├── notification_service.py  Email/SMS
│   │   └── auth_decorators.py   JWT decorators
│   └── __init__.py              App factory
├── frontend/                     React application
│   ├── src/
│   │   ├── components/          Reusable components
│   │   ├── pages/               Page components
│   │   ├── services/            API services
│   │   ├── context/             React context
│   │   └── App.js               Main app
│   └── package.json
├── ml/                           Machine learning
│   ├── data_processing/         Data preprocessing
│   ├── models/                  ML models
│   └── utils/                   ML utilities
├── scripts/                      Database scripts
│   ├── init_sqlite.py          Initialize database
│   ├── seed_data.py            Seed products/suppliers
│   └── seed_customers_batches.py Seed customers/batches
├── instance/                     SQLite database
│   └── inventory.db
├── .env.example                 Environment variables template
├── requirements.txt             Python dependencies
├── run_sqlite.py               Start backend (SQLite)
└── README.md                   This file

========================================
API ENDPOINTS
========================================

Base URL: http://localhost:5000/api

Authentication
- POST /auth/login - User login
- POST /auth/register - User registration
- POST /auth/refresh - Refresh token
- GET /auth/me - Get current user

Products
- GET /products - List all products
- POST /products - Create product
- PUT /products/:id - Update product
- DELETE /products/:id - Delete product

Inventory
- GET /inventory/items - List inventory
- POST /inventory/items/:id/adjust - Adjust stock
- POST /inventory/items/:id/sale - Record sale
- GET /inventory/low-stock - Low stock items

Customers
- GET /customers - List customers
- POST /customers - Create customer
- PUT /customers/:id - Update customer
- POST /customers/:id/loyalty - Add/redeem loyalty points
- POST /customers/:id/special-price - Set special price
- GET /customers/top - Top customers

Batches
- GET /batches - List batches
- POST /batches - Create batch
- GET /batches/expiring - Expiring batches
- GET /batches/valuation?method=fifo - Inventory valuation (FIFO/LIFO)
- POST /batches/allocate - Allocate batch for sale

Sales
- GET /sales - Sales history
- GET /sales/analytics/daily - Daily sales
- GET /sales/analytics/monthly - Monthly sales

Suppliers
- GET /suppliers - List suppliers
- POST /suppliers - Create supplier
- POST /suppliers/:id/contact - Contact supplier (Email/SMS)

Competitors
- GET /competitors - List competitors
- GET /competitors/:id - Competitor details
- GET /competitors/:id/products - Competitor products
- GET /competitors/:id/sales - Competitor sales

Forecasting
- POST /forecast/predict/:id - Generate forecast
- GET /forecast/model-info - Model information

Alerts
- GET /alerts - Active alerts
- POST /alerts/check-stock-levels - Check stock levels

Analytics
- GET /analytics/dashboard - Dashboard statistics

Users (Admin only)
- GET /users - List users
- POST /users - Create user
- PUT /users/:id - Update user

========================================
KEY FEATURES DETAILS
========================================

Customer Management
- Customer Types: Regular, VIP, Wholesale
- Loyalty Points: Earn on purchases, redeem for discounts
- Special Pricing: Set custom prices per customer per product
- Discount Tiers: Percentage-based discounts
- Credit Management: Track credit limits and outstanding balances
- Purchase History: Complete transaction history

Batch/Lot Tracking
- Batch Numbers: Unique identifiers for each batch
- Expiry Management: Track expiry dates with alerts
- FIFO/LIFO: Choose inventory valuation method
- Cost Tracking: Cost per unit for accurate valuation
- Supplier Linkage: Track which supplier provided each batch
- Expiry Alerts: 30-day, 7-day, and expired warnings

Demand Forecasting
- ML Models: Random Forest, Gradient Boosting, Linear Regression
- Best Model Selection: Automatically selects best performing model
- Historical Analysis: Uses 12 months of sales data
- Accuracy Metrics: MAE, RMSE, R² score
- Visual Predictions: Charts showing predicted vs actual

Competitor Intelligence
- Category Filtering: See competitors in your product categories
- Sales Tracking: Monitor competitor sales performance
- Price Comparison: Compare product pricing
- Market Analysis: Understand competitive landscape

========================================
CONFIGURATION
========================================

Environment Variables (.env)

DATABASE_URL=sqlite:///instance/inventory.db
or for PostgreSQL:
DATABASE_URL=postgresql://user:pass@localhost:5432/inventory_db

JWT_SECRET_KEY=your-secret-key-change-in-production

Email (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

SMS (Africa's Talking)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-api-key

Application
FLASK_ENV=development
FLASK_DEBUG=True

========================================
TESTING
========================================

Backend Tests
pytest
pytest tests/test_inventory.py

Frontend Tests
cd frontend
npm test

========================================
ML MODEL TRAINING
========================================

Quick Training (Recommended)

Preprocess data
python ml/data_processing/preprocess_simple.py

Train models (Random Forest, Gradient Boosting, Linear Regression)
python ml/models/train_simple.py

Evaluate models
python ml/models/evaluate_model.py

Model Performance
- Random Forest: MAE ~6.5, Best for complex patterns
- Gradient Boosting: MAE ~6.3, Best overall accuracy
- Linear Regression: MAE ~6.2, Best for simple trends (selected as best)

========================================
TROUBLESHOOTING
========================================

Backend won't start
python --version  (Should be 3.11+)
pip install -r requirements.txt
python scripts/init_sqlite.py

Frontend errors
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start

Database issues
rm instance/inventory.db
python scripts/init_sqlite.py
python scripts/seed_data.py
python scripts/seed_customers_batches.py

ML model not loading
python ml/data_processing/preprocess_simple.py
python ml/models/train_simple.py

========================================
SECURITY
========================================

- JWT-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- SQL injection protection via SQLAlchemy
- CORS configuration
- Environment variable protection

========================================
LICENSE
========================================

Proprietary - All rights reserved

========================================
SUPPORT
========================================

For issues or questions:
1. Check documentation files (QUICKSTART.md, CUSTOMER_BATCH_FEATURES.md)
2. Review API endpoints above
3. Check troubleshooting section

Built with modern technologies for efficient inventory management.
