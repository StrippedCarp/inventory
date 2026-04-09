#!/usr/bin/env python3
"""Database initialization script"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sales_transaction import SalesTransaction
from app.models import PurchaseOrder, Forecast, Alert

def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (for clean setup)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Verify tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")

if __name__ == '__main__':
    init_database()