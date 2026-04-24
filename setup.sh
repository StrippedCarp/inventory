#!/bin/bash

echo "========================================"
echo " Inventory Management System Setup"
echo "========================================"
echo ""

echo "[1/3] Starting Docker containers..."
docker-compose up -d

echo ""
echo "[2/3] Waiting for containers to be ready..."
sleep 30

echo ""
echo "[3/3] Initializing database..."
docker-compose exec backend python scripts/init_sqlite.py
docker-compose exec backend python scripts/add_activity_logs_table.py
docker-compose exec backend python scripts/add_org_to_competitors.py
docker-compose exec backend python scripts/seed_activities.py

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:5000"
echo ""
echo "  Login credentials:"
echo "    Username: admin"
echo "    Password: password123"
echo ""
echo "Opening application in browser..."
sleep 2

# Open browser based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:3000
fi
