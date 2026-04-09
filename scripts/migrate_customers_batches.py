"""  
Migration script to add customer management and batch tracking tables
Run this after updating the models
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.customer import Customer, CustomerPricing, LoyaltyTransaction
from app.models.batch import Batch, BatchTransaction

def migrate():
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        print("Creating new tables...")
        
        # Create tables
        db.create_all()
        
        print("[OK] Tables created successfully!")
        print("\nNew tables added:")
        print("  - customers")
        print("  - customer_pricing")
        print("  - loyalty_transactions")
        print("  - batches")
        print("  - batch_transactions")
        print("\nNote: sales_transactions table updated with customer_id column")

if __name__ == '__main__':
    migrate()
