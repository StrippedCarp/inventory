"""
Migration script to add Competitors and SupplierContact tables
Run this after updating models
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.competitor import Competitor, CompetitorSales, CompetitorProduct
from app.models.supplier_contact import SupplierContact
from datetime import datetime, date
import random

def seed_competitors():
    """Seed sample competitor data"""
    
    # Sample competitors
    competitors_data = [
        {
            'business_name': 'Fresh Groceries Ltd',
            'owner_name': 'Jane Doe',
            'category': 'grocery',
            'location': 'Nairobi CBD',
            'phone': '+254-712-345678',
            'email': 'info@freshgroceries.co.ke'
        },
        {
            'business_name': 'Green Market',
            'owner_name': 'John Smith',
            'category': 'grocery',
            'location': 'Westlands',
            'phone': '+254-723-456789',
            'email': 'contact@greenmarket.co.ke'
        },
        {
            'business_name': 'Tech Supplies Kenya',
            'owner_name': 'Mary Johnson',
            'category': 'electronics',
            'location': 'Kilimani',
            'phone': '+254-734-567890',
            'email': 'sales@techsupplies.co.ke'
        }
    ]
    
    for comp_data in competitors_data:
        competitor = Competitor(**comp_data)
        db.session.add(competitor)
        db.session.flush()
        
        # Add sales data
        sales = CompetitorSales(
            competitor_id=competitor.id,
            date=date.today(),
            daily_sales=random.randint(10000, 50000),
            monthly_sales=random.randint(300000, 1500000),
            yearly_sales=random.randint(3600000, 18000000)
        )
        db.session.add(sales)
        
        # Add sample products
        products = [
            {'product_name': 'Product A', 'category': comp_data['category'], 'price': random.randint(100, 5000)},
            {'product_name': 'Product B', 'category': comp_data['category'], 'price': random.randint(100, 5000)},
            {'product_name': 'Product C', 'category': comp_data['category'], 'price': random.randint(100, 5000)},
        ]
        
        for prod_data in products:
            product = CompetitorProduct(competitor_id=competitor.id, **prod_data)
            db.session.add(product)
    
    db.session.commit()
    print("Competitor data seeded successfully")

def run_migration():
    """Run the migration"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        print("Creating new tables...")
        db.create_all()
        print("Tables created successfully")
        
        print("\nSeeding competitor data...")
        seed_competitors()
        
        print("\nMigration completed successfully!")

if __name__ == '__main__':
    run_migration()
