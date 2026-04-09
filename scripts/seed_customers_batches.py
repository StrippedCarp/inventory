"""
Seed script for customers and batches
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.customer import Customer, LoyaltyTransaction
from app.models.batch import Batch
from app.models.product import Product
from app.models.supplier import Supplier
from datetime import datetime, timedelta
import random

def seed_customers_batches():
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        print("Seeding customers and batches...")
        
        # Create sample customers
        customers_data = [
            {
                'name': 'John Kamau', 'email': 'john.kamau@email.com', 'phone': '0712345678',
                'customer_type': 'regular', 'discount_percentage': 0, 'address': 'Nairobi, Kenya'
            },
            {
                'name': 'Mary Wanjiku', 'email': 'mary.w@email.com', 'phone': '0723456789',
                'customer_type': 'vip', 'discount_percentage': 10, 'address': 'Mombasa, Kenya'
            },
            {
                'name': 'Peter Omondi', 'email': 'peter.o@email.com', 'phone': '0734567890',
                'customer_type': 'wholesale', 'discount_percentage': 15, 'address': 'Kisumu, Kenya',
                'credit_limit': 50000
            },
            {
                'name': 'Grace Akinyi', 'email': 'grace.a@email.com', 'phone': '0745678901',
                'customer_type': 'regular', 'discount_percentage': 0, 'address': 'Nakuru, Kenya'
            },
            {
                'name': 'David Mwangi', 'email': 'david.m@email.com', 'phone': '0756789012',
                'customer_type': 'vip', 'discount_percentage': 10, 'address': 'Eldoret, Kenya'
            },
        ]
        
        customers = []
        for data in customers_data:
            # Check if customer already exists
            existing = Customer.query.filter_by(email=data['email']).first()
            if existing:
                customers.append(existing)
                continue
                
            customer = Customer(**data)
            customer.loyalty_points = random.randint(0, 500)
            customer.total_purchases = random.uniform(5000, 50000)
            db.session.add(customer)
            customers.append(customer)
        
        db.session.commit()
        print(f"[OK] Created {len(customers)} customers")
        
        # Add loyalty transactions
        for customer in customers[:3]:
            for i in range(3):
                transaction = LoyaltyTransaction(
                    customer_id=customer.id,
                    points=random.randint(10, 100),
                    transaction_type='earned',
                    description=f'Purchase #{random.randint(1000, 9999)}'
                )
                db.session.add(transaction)
        
        db.session.commit()
        print("[OK] Created loyalty transactions")
        
        # Create batches for existing products
        products = Product.query.limit(10).all()
        suppliers = Supplier.query.all()
        
        if not products:
            print("[WARNING] No products found. Run seed_data.py first.")
            return
        
        batches = []
        for product in products:
            # Create 2-3 batches per product
            for i in range(random.randint(2, 3)):
                batch_number = f"BATCH-{product.id}-{datetime.now().year}-{random.randint(1000, 9999)}"
                
                # Random dates
                received_date = datetime.now() - timedelta(days=random.randint(1, 90))
                manufacture_date = received_date - timedelta(days=random.randint(30, 180))
                expiry_date = manufacture_date + timedelta(days=random.randint(180, 730))
                
                batch = Batch(
                    product_id=product.id,
                    batch_number=batch_number,
                    quantity=random.randint(50, 500),
                    cost_per_unit=float(product.unit_price) * random.uniform(0.5, 0.8),  # Cost is 50-80% of selling price
                    manufacture_date=manufacture_date.date(),
                    expiry_date=expiry_date.date(),
                    supplier_id=random.choice(suppliers).id if suppliers else None,
                    received_date=received_date,
                    status='active'
                )
                db.session.add(batch)
                batches.append(batch)
        
        db.session.commit()
        print(f"[OK] Created {len(batches)} batches")
        
        # Create some expiring batches
        for i in range(3):
            product = random.choice(products)
            batch_number = f"BATCH-EXP-{datetime.now().year}-{random.randint(1000, 9999)}"
            
            expiry_date = datetime.now() + timedelta(days=random.randint(1, 20))
            
            batch = Batch(
                product_id=product.id,
                batch_number=batch_number,
                quantity=random.randint(10, 50),
                cost_per_unit=float(product.unit_price) * 0.6,
                manufacture_date=(datetime.now() - timedelta(days=300)).date(),
                expiry_date=expiry_date.date(),
                supplier_id=random.choice(suppliers).id if suppliers else None,
                status='active'
            )
            db.session.add(batch)
        
        db.session.commit()
        print("[OK] Created expiring batches")
        
        print("\n[SUCCESS] Customer and batch seeding completed!")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(batches) + 3} batches")

if __name__ == '__main__':
    seed_customers_batches()
