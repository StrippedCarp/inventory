QUICK START GUIDE

Get the inventory management system running in 5 minutes.

========================================
PREREQUISITES
========================================

- Python 3.11+
- Node.js 16+

========================================
SETUP STEPS
========================================

Backend Setup

Install dependencies
pip install -r requirements.txt

Initialize database and seed data
python scripts/init_sqlite.py
python scripts/seed_data.py
python scripts/seed_customers_batches.py

Start backend
python run_sqlite.py

Backend will run on http://localhost:5000

Frontend Setup (New Terminal)

cd frontend
npm install
npm start

Frontend will run on http://localhost:3000

Login Credentials

- Admin: admin / password123
- Manager: manager / password123
- Viewer: viewer / password123

========================================
OPTIONAL: TRAIN ML MODELS
========================================

Preprocess data
python ml/data_processing/preprocess_simple.py

Train models
python ml/models/train_simple.py

========================================
QUICK COMMANDS
========================================

Reset Database
rm instance/inventory.db
python scripts/init_sqlite.py
python scripts/seed_data.py
python scripts/seed_customers_batches.py

Cleanup
cleanup.bat  (Windows)

========================================
WHAT'S INCLUDED
========================================

Sample Data
- 25 products across 5 categories
- 10 suppliers
- 8,617 sales transactions (12 months)
- 5 customers with loyalty points
- 26 product batches with expiry dates
- 3 competitors with sales data

Features Available
- Inventory tracking
- Product management
- Customer management with loyalty
- Batch tracking with FIFO/LIFO
- Sales analytics
- Demand forecasting
- Supplier contact (Email/SMS)
- Competitor intelligence
- Low stock alerts

========================================
NEXT STEPS
========================================

1. Explore the dashboard at /dashboard
2. Add your own products at /products
3. Create customers at /customers
4. Track batches at /batches
5. View analytics at /analytics

========================================
NEED HELP?
========================================

- Full documentation: README.md
- Customer/Batch features: CUSTOMER_BATCH_FEATURES.md
- Project structure: PROJECT_STRUCTURE.md

========================================
API TESTING
========================================

Base URL: http://localhost:5000/api

Get products
curl http://localhost:5000/api/products

Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'

========================================
TROUBLESHOOTING
========================================

Backend won't start?
pip install -r requirements.txt
python scripts/init_sqlite.py

Frontend errors?
cd frontend
rm -rf node_modules
npm install

Database issues?
rm instance/inventory.db
python scripts/init_sqlite.py
python scripts/seed_data.py

You're ready to go.
