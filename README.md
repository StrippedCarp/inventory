# AI-Powered Inventory Management System

Complete inventory management system with ML-based demand forecasting, customer management, batch tracking, and organization-based multi-tenancy for SMEs.

## Quick Start with Docker (Recommended) 🐳

### Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Start Docker Desktop and wait for "Engine running" status

### Automated Setup (Easiest)
```bash
# Clone repository
git clone https://github.com/StrippedCarp/inventory.git
cd inventory

# Windows
setup.bat

# Mac/Linux
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# 1. Start containers
docker-compose up -d

# 2. Initialize database (first time only)
docker-compose exec backend python scripts/init_sqlite.py
docker-compose exec backend python scripts/add_activity_logs_table.py
docker-compose exec backend python scripts/add_org_to_competitors.py
docker-compose exec backend python scripts/seed_activities.py
```

**Access**: http://localhost:3000  
**Login**: username: `admin`, password: `password123`

### Docker Commands
```bash
docker-compose up -d      # Start
docker-compose down       # Stop
docker-compose logs -f    # View logs
docker-compose restart    # Restart
```

## Traditional Setup (Without Docker)

```bash
# Backend setup
pip install -r requirements.txt
python scripts/init_sqlite.py
python scripts/add_activity_logs_table.py
python scripts/add_org_to_competitors.py
python scripts/seed_activities.py
python run_sqlite.py

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

## Key Features

✅ **Inventory Management** - Real-time stock tracking with alerts  
✅ **Multi-Tenancy** - Organization-based data isolation  
✅ **Activity Feed** - Comprehensive audit trail  
✅ **Team Collaboration** - Invitation system with role-based access  
✅ **ML Forecasting** - Demand prediction with multiple models  
✅ **Customer Management** - Loyalty points and special pricing  
✅ **Supplier Management** - Contact tracking and ratings  
✅ **Competitor Intelligence** - Market analysis and price comparison  
✅ **Batch Tracking** - FIFO/LIFO with expiry management  

## User Roles

- **Admin**: Full access, manage users and organization
- **Manager**: Edit data, view everything
- **Viewer**: Read-only access

## Documentation

📖 **[Complete System Documentation](SYSTEM_DOCUMENTATION.md)** - Full feature guide  
📊 **[Activity Feed Guide](ACTIVITY_FEED.md)** - Activity logging details  
🏢 **[Organization Management](ORGANIZATION_MANAGEMENT.md)** - Multi-tenancy guide  
🐳 **[Docker Setup Guide](DOCKER_SETUP.md)** - Containerized deployment  

## Tech Stack

**Backend**: Python 3.11, Flask, SQLAlchemy, JWT, Scikit-learn  
**Frontend**: React 18, Material-UI, Axios, Chart.js  
**Database**: SQLite (dev) / PostgreSQL (prod)  

## API Endpoints

```
POST   /api/auth/login
GET    /api/products
GET    /api/inventory/items
GET    /api/customers
GET    /api/suppliers
GET    /api/competitors
GET    /api/activity
GET    /api/organizations/settings
```

Full API reference in [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)

## Project Structure

```
inventory/
├── app/              # Backend (Flask)
├── frontend/         # Frontend (React)
├── ml/               # Machine learning models
├── scripts/          # Database migrations
└── instance/         # SQLite database
```

## Troubleshooting

**Backend won't start**: `pip install -r requirements.txt`  
**Frontend errors**: `cd frontend && npm install`  
**Database issues**: `python scripts/init_sqlite.py`  
**Missing data**: Run migration scripts in order  

See [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md) for detailed troubleshooting.

## License

Proprietary - All rights reserved

---

Built with modern technologies for efficient inventory management and team collaboration.
