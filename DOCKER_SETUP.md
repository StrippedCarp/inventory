# Docker Setup Guide

## Prerequisites

- Docker Desktop installed (https://www.docker.com/products/docker-desktop)
- Docker Compose (included with Docker Desktop)

## Quick Start

### 1. Build and Start Containers

```bash
docker-compose up --build
```

This will:
- Build the backend (Flask) container
- Build the frontend (React) container
- Start both services
- Backend runs on http://localhost:5000
- Frontend runs on http://localhost:3000

### 2. Initialize Database (First Time Only)

Open a new terminal and run:

```bash
# Initialize database
docker-compose exec backend python scripts/init_sqlite.py

# Add activity logs table
docker-compose exec backend python scripts/add_activity_logs_table.py

# Add organization to competitors
docker-compose exec backend python scripts/add_org_to_competitors.py

# Seed sample data
docker-compose exec backend python scripts/seed_activities.py
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **Login**: username: `admin`, password: `password123`

## Docker Commands

### Start Services (Detached Mode)
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Rebuild Containers
```bash
docker-compose up --build
```

### Execute Commands in Container
```bash
# Backend
docker-compose exec backend python scripts/your_script.py

# Frontend
docker-compose exec frontend npm install new-package
```

### Restart Services
```bash
docker-compose restart
```

### Remove Containers and Volumes
```bash
docker-compose down -v
```

## Production Deployment

For production, create a separate `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - REACT_APP_API_URL=${API_URL}
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "5001:5000"  # Backend
  - "3001:3000"  # Frontend
```

### Database Not Persisting
- Check that `./instance` directory exists
- Verify volume mount in docker-compose.yml

### Frontend Not Hot Reloading
- Ensure `CHOKIDAR_USEPOLLING=true` is set
- Check volume mounts are correct

### Permission Issues (Linux/Mac)
```bash
sudo chown -R $USER:$USER instance/
```

## Environment Variables

Create `.env` file in root directory:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
FLASK_ENV=development
REACT_APP_API_URL=http://localhost:5000/api
```

## Database Backup

```bash
# Backup
docker-compose exec backend cp /app/instance/inventory.db /app/instance/backup.db

# Copy to host
docker cp inventory-backend:/app/instance/inventory.db ./backup.db
```

## Notes

- SQLite database is stored in `./instance` directory (persisted via volume)
- Hot reload enabled for both backend and frontend during development
- Frontend uses polling for file changes (works better in Docker)
- Network `inventory-network` allows containers to communicate
