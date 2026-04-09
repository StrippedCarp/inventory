PROJECT STRUCTURE

========================================
DIRECTORY LAYOUT
========================================

inventory-main/
├── app/                          Main application (unified backend)
│   ├── models/                   Database models
│   │   ├── __init__.py          Alert, Forecast, PurchaseOrder models
│   │   ├── batch.py             Batch tracking
│   │   ├── competitor.py        Competitor intelligence
│   │   ├── customer.py          Customer management
│   │   ├── inventory.py         Inventory model
│   │   ├── product.py           Product model
│   │   ├── sales_transaction.py Sales model
│   │   ├── supplier.py          Supplier model
│   │   ├── supplier_contact.py  Supplier contact tracking
│   │   └── user.py              User model
│   ├── routes/                   API endpoints
│   │   ├── admin_competitors.py Admin competitor management
│   │   ├── alerts.py            Alert management
│   │   ├── analytics.py         Analytics & reports
│   │   ├── auth.py              Authentication
│   │   ├── batches.py           Batch tracking
│   │   ├── competitors.py       Competitor data
│   │   ├── customers.py         Customer management
│   │   ├── forecast.py          Demand forecasting
│   │   ├── inventory.py         Inventory operations
│   │   ├── orders.py            Purchase orders
│   │   ├── products.py          Product management
│   │   ├── sales.py             Sales transactions
│   │   ├── suppliers.py         Supplier management
│   │   └── users.py             User management
│   ├── utils/                    Utilities
│   │   ├── auth_decorators.py   Auth helpers
│   │   └── notification_service.py Email/SMS notifications
│   ├── __init__.py              App factory
│   └── config.py                Configuration
│
├── frontend/                     React frontend
│   ├── public/                   Static files
│   ├── src/
│   │   ├── components/          Reusable components
│   │   │   ├── Layout.js        Main layout
│   │   │   └── ProtectedRoute.js Route protection
│   │   ├── context/             React context
│   │   │   └── AuthContext.js   Auth state
│   │   ├── pages/               Page components
│   │   │   ├── AlertsPage.js    Alerts management
│   │   │   ├── AnalyticsPage.js Analytics dashboard
│   │   │   ├── BatchesPage.js   Batch tracking
│   │   │   ├── CompetitorsPage.js Competitor intelligence
│   │   │   ├── CustomersPage.js Customer management
│   │   │   ├── Dashboard.js     Main dashboard
│   │   │   ├── ForecastPage.js  Demand forecasting
│   │   │   ├── InventoryPage.js Inventory management
│   │   │   ├── Login.js         Login page
│   │   │   ├── ProductsPage.js  Product management
│   │   │   ├── SalesPage.js     POS system
│   │   │   ├── SuppliersPage.js Supplier management
│   │   │   └── UsersPage.js     User management
│   │   ├── services/            API services
│   │   │   └── api.js           API client
│   │   ├── App.js               Main app component
│   │   └── index.js             Entry point
│   ├── package.json             Dependencies
│   └── package-lock.json
│
├── ml/                           Machine learning
│   ├── data/                     Training data
│   │   ├── metadata.pkl
│   │   ├── scaler.pkl
│   │   ├── test_data.npz
│   │   ├── train_data.npz
│   │   └── val_data.npz
│   ├── data_processing/          Data preprocessing
│   │   ├── preprocess_data.py
│   │   ├── preprocess_simple.py
│   │   └── visualize_data.py
│   ├── models/                   Trained models
│   │   ├── best_forecaster.pkl
│   │   ├── evaluate_model.py
│   │   ├── gradient_boost_forecaster.pkl
│   │   ├── linear_forecaster.pkl
│   │   ├── random_forest_forecaster.pkl
│   │   ├── train_lstm.py
│   │   └── train_simple.py
│   ├── results/                  Model results
│   │   └── model_comparison.pkl
│   └── utils/                    ML utilities
│       └── ml_utils.py
│
├── scripts/                      Database scripts
│   ├── init_db.py               Initialize database
│   ├── init_sqlite.py           SQLite setup
│   ├── migrate_competitors.py   Competitor migration
│   ├── migrate_customers_batches.py Customer/batch migration
│   ├── seed_customers_batches.py Seed customers/batches
│   ├── seed_data.py             Seed sample data
│   └── update_competitor_data.py Update competitor data
│
├── instance/                     SQLite database
│   └── inventory.db             Local database file
│
├── .env                          Environment variables
├── .env.example                  Environment template
├── docker-compose.yml            Docker services
├── requirements.txt              Python dependencies
├── run_sqlite.py                 Run with SQLite
├── cleanup.bat                   Cleanup script
├── CUSTOMER_BATCH_FEATURES.md    Customer/Batch documentation
├── QUICKSTART.md                 Quick start guide
├── PROJECT_STRUCTURE.md          This file
└── README.md                     Main documentation

========================================
KEY DIRECTORIES
========================================

/app - Unified Backend
- Single Flask application with all routes
- SQLAlchemy models for database
- JWT authentication
- RESTful API endpoints

/frontend - React Application
- Material-UI components
- Role-based access control
- Real-time inventory updates
- POS system integration

/ml - Machine Learning
- Random Forest, Gradient Boosting, Linear Regression models
- Data preprocessing pipelines
- Model evaluation tools
- Trained model storage

/scripts - Database Management
- Database initialization
- Sample data seeding
- Migration scripts

========================================
RUNNING THE APPLICATION
========================================

Development (SQLite)
python run_sqlite.py
cd frontend && npm start

Production (PostgreSQL)
docker-compose up -d
python run_sqlite.py
cd frontend && npm start

========================================
API ENDPOINTS
========================================

All endpoints are prefixed with /api:

- /auth - Authentication
- /users - User management (admin only)
- /products - Product CRUD
- /inventory - Inventory operations
- /sales - Sales transactions
- /suppliers - Supplier management
- /customers - Customer management
- /batches - Batch tracking
- /competitors - Competitor intelligence
- /alerts - Alert system
- /forecast - Demand forecasting
- /analytics - Reports & analytics
- /orders - Purchase orders

========================================
DATABASE MODELS
========================================

Core Models
- User - Authentication and authorization
- Product - Product catalog
- Inventory - Stock levels
- SalesTransaction - Sales records
- Supplier - Supplier database
- Alert - Stock alerts
- Forecast - Demand predictions
- PurchaseOrder - Purchase orders

Advanced Models
- Customer - Customer database
- CustomerPricing - Special pricing
- LoyaltyTransaction - Loyalty points
- Batch - Batch tracking
- BatchTransaction - Batch history
- Competitor - Competitor data
- CompetitorSales - Competitor sales
- CompetitorProduct - Competitor products
- SupplierContact - Supplier communications

========================================
FRONTEND PAGES
========================================

Public Pages
- Login - User authentication

Protected Pages
- Dashboard - Overview and statistics
- Inventory - Stock management
- Products - Product catalog
- Sales - POS system
- Customers - Customer management
- Batches - Batch tracking
- Suppliers - Supplier database
- Competitors - Market intelligence
- Forecast - Demand predictions
- Alerts - Stock alerts
- Analytics - Reports and insights
- Users - User management (admin only)

========================================
CONFIGURATION FILES
========================================

.env - Environment variables
- Database connection
- JWT secret key
- Email/SMS credentials
- Application settings

requirements.txt - Python dependencies
- Flask and extensions
- SQLAlchemy
- JWT authentication
- ML libraries (scikit-learn, TensorFlow)

package.json - Frontend dependencies
- React and React Router
- Material-UI
- Axios
- Chart.js

docker-compose.yml - Docker services
- PostgreSQL database
- Redis cache (optional)
- Application container

========================================
SCRIPTS
========================================

Database Scripts
- init_sqlite.py - Create SQLite database
- seed_data.py - Populate with sample data
- seed_customers_batches.py - Add customers and batches
- migrate_*.py - Database migrations

ML Scripts
- preprocess_simple.py - Prepare training data
- train_simple.py - Train forecasting models
- evaluate_model.py - Evaluate model performance

Utility Scripts
- cleanup.bat - Clean temporary files
- run_sqlite.py - Start backend with SQLite

========================================
DEPLOYMENT
========================================

Development
- SQLite database
- Flask development server
- React development server

Production
- PostgreSQL database
- Gunicorn WSGI server
- Nginx reverse proxy
- Docker containers

========================================
TESTING
========================================

Backend Tests
- Unit tests for models
- Integration tests for routes
- API endpoint tests

Frontend Tests
- Component tests
- Integration tests
- E2E tests

ML Tests
- Model accuracy tests
- Data preprocessing tests
- Prediction validation

========================================
DOCUMENTATION
========================================

README.md - Main documentation
- Features overview
- Installation guide
- API reference
- Configuration

QUICKSTART.md - Quick start guide
- 5-minute setup
- Basic usage
- Common commands

CUSTOMER_BATCH_FEATURES.md - Advanced features
- Customer management
- Batch tracking
- Usage examples

PROJECT_STRUCTURE.md - This file
- Directory layout
- File descriptions
- Architecture overview
