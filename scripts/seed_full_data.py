#!/usr/bin/env python3
"""Comprehensive seed script with full data"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.batch import Batch
from app.models.competitor import Competitor, CompetitorProduct, CompetitorSales
from app.models.sales_transaction import SalesTransaction
from app.models import Alert
from datetime import datetime, date, timedelta
import random

def seed_full_data():
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        print("Seeding full database...")
        
        # Get or create users
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@test.com', role='admin')
            admin.set_password('password123')
            db.session.add(admin)
        
        manager = User.query.filter_by(username='manager').first()
        if not manager:
            manager = User(username='manager', email='manager@test.com', role='manager')
            manager.set_password('password123')
            db.session.add(manager)
        
        viewer = User.query.filter_by(username='viewer').first()
        if not viewer:
            viewer = User(username='viewer', email='viewer@test.com', role='viewer')
            viewer.set_password('password123')
            db.session.add(viewer)
        
        db.session.commit()
        print(f"Created 3 users")
        
        # Create suppliers for admin
        suppliers_data = [
            {'name': 'TechCorp Solutions', 'contact_person': 'John Smith', 'email': 'john@techcorp.com', 'phone': '555-0101'},
            {'name': 'Global Electronics', 'contact_person': 'Sarah Johnson', 'email': 'sarah@globalelec.com', 'phone': '555-0102'},
            {'name': 'Fashion Forward Inc', 'contact_person': 'Mike Chen', 'email': 'mike@fashionfw.com', 'phone': '555-0103'},
            {'name': 'Food Distributors LLC', 'contact_person': 'Lisa Brown', 'email': 'lisa@fooddist.com', 'phone': '555-0104'},
            {'name': 'Hardware Supplies Co', 'contact_person': 'David Wilson', 'email': 'david@hwsupply.com', 'phone': '555-0105'}
        ]
        
        suppliers = []
        for sdata in suppliers_data:
            supplier = Supplier(**sdata, user_id=admin.id)
            db.session.add(supplier)
            suppliers.append(supplier)
        
        db.session.commit()
        print(f"Created {len(suppliers)} suppliers")
        
        # Create products for admin
        products_data = [
            {'sku': 'ELEC001', 'name': 'Wireless Headphones', 'category': 'Electronics', 'price': 79.99, 'supplier': 0},
            {'sku': 'ELEC002', 'name': 'USB-C Cable', 'category': 'Electronics', 'price': 12.99, 'supplier': 0},
            {'sku': 'ELEC003', 'name': 'Power Bank', 'category': 'Electronics', 'price': 34.99, 'supplier': 1},
            {'sku': 'ELEC004', 'name': 'Wireless Mouse', 'category': 'Electronics', 'price': 24.99, 'supplier': 1},
            {'sku': 'ELEC005', 'name': 'Bluetooth Speaker', 'category': 'Electronics', 'price': 45.99, 'supplier': 0},
            {'sku': 'CLTH001', 'name': 'Cotton T-Shirt', 'category': 'Clothing', 'price': 19.99, 'supplier': 2},
            {'sku': 'CLTH002', 'name': 'Denim Jeans', 'category': 'Clothing', 'price': 49.99, 'supplier': 2},
            {'sku': 'CLTH003', 'name': 'Running Shoes', 'category': 'Clothing', 'price': 89.99, 'supplier': 2},
            {'sku': 'FOOD001', 'name': 'Organic Pasta', 'category': 'Food', 'price': 3.99, 'supplier': 3},
            {'sku': 'FOOD002', 'name': 'Olive Oil', 'category': 'Food', 'price': 12.99, 'supplier': 3},
            {'sku': 'HARD001', 'name': 'Hammer', 'category': 'Hardware', 'price': 24.99, 'supplier': 4},
            {'sku': 'HARD002', 'name': 'Screwdriver Set', 'category': 'Hardware', 'price': 34.99, 'supplier': 4}
        ]
        
        products = []
        for pdata in products_data:
            product = Product(
                sku=pdata['sku'],
                name=pdata['name'],
                category=pdata['category'],
                unit_price=pdata['price'],
                supplier_id=suppliers[pdata['supplier']].id,
                user_id=admin.id,
                reorder_point=20,
                safety_stock=10
            )
            db.session.add(product)
            db.session.flush()
            products.append(product)
            
            # Create inventory
            stock = random.randint(15, 100)
            inventory = Inventory(
                product_id=product.id,
                quantity_on_hand=stock,
                warehouse_location=f"{random.choice(['A', 'B', 'C'])}{random.randint(1, 5)}"
            )
            db.session.add(inventory)
        
        db.session.commit()
        print(f"Created {len(products)} products with inventory")
        
        # Create customers for admin
        customers_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'phone': '555-1001', 'type': 'regular'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '555-1002', 'type': 'vip'},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'phone': '555-1003', 'type': 'wholesale'},
            {'name': 'Alice Brown', 'email': 'alice@example.com', 'phone': '555-1004', 'type': 'regular'},
            {'name': 'Charlie Wilson', 'email': 'charlie@example.com', 'phone': '555-1005', 'type': 'vip'}
        ]
        
        customers = []
        for cdata in customers_data:
            customer = Customer(
                name=cdata['name'],
                email=cdata['email'],
                phone=cdata['phone'],
                customer_type=cdata['type'],
                loyalty_points=random.randint(0, 500),
                user_id=admin.id
            )
            db.session.add(customer)
            customers.append(customer)
        
        db.session.commit()
        print(f"Created {len(customers)} customers")
        
        # Create batches for products
        batches = []
        for product in products[:6]:
            batch = Batch(
                product_id=product.id,
                batch_number=f"BATCH-{product.sku}-001",
                quantity=50,
                cost_per_unit=float(product.unit_price) * 0.6,
                expiry_date=date.today() + timedelta(days=random.randint(30, 365)),
                supplier_id=product.supplier_id
            )
            db.session.add(batch)
            batches.append(batch)
        
        db.session.commit()
        print(f"Created {len(batches)} batches")
        
        # Create competitors
        competitors_data = [
            {'business_name': 'TechMart', 'location': 'Downtown', 'category': 'Electronics'},
            {'business_name': 'Fashion Hub', 'location': 'Mall', 'category': 'Clothing'},
            {'business_name': 'Food Paradise', 'location': 'Westside', 'category': 'Food'}
        ]
        
        competitors = []
        for cdata in competitors_data:
            competitor = Competitor(
                business_name=cdata['business_name'],
                location=cdata['location'],
                category=cdata['category']
            )
            db.session.add(competitor)
            db.session.flush()
            competitors.append(competitor)
            
            # Add competitor products
            for i in range(3):
                comp_product = CompetitorProduct(
                    competitor_id=competitor.id,
                    product_name=f"{cdata['category']} Item {i+1}",
                    category=cdata['category'],
                    price=random.uniform(10, 100)
                )
                db.session.add(comp_product)
            
            # Add competitor sales
            for days_ago in range(30):
                sale_date = date.today() - timedelta(days=days_ago)
                comp_sales = CompetitorSales(
                    competitor_id=competitor.id,
                    date=sale_date,
                    daily_sales=random.uniform(500, 5000)
                )
                db.session.add(comp_sales)
        
        db.session.commit()
        print(f"Created {len(competitors)} competitors with products and sales")
        
        # Create sales transactions (last 90 days)
        for days_ago in range(90):
            sale_date = date.today() - timedelta(days=days_ago)
            num_sales = random.randint(2, 8)
            
            for _ in range(num_sales):
                product = random.choice(products)
                quantity = random.randint(1, 5)
                
                transaction = SalesTransaction(
                    product_id=product.id,
                    quantity_sold=quantity,
                    sale_date=sale_date,
                    unit_price=product.unit_price,
                    total_amount=quantity * product.unit_price
                )
                db.session.add(transaction)
        
        db.session.commit()
        print("Created 90 days of sales transactions")
        
        # Create alerts for low stock
        low_stock_products = [p for p in products if Inventory.query.filter_by(product_id=p.id).first().quantity_on_hand < 25]
        for product in low_stock_products[:3]:
            alert = Alert(
                product_id=product.id,
                alert_type='low_stock',
                severity='warning',
                message=f'{product.name} stock is low',
                status='active'
            )
            db.session.add(alert)
        
        db.session.commit()
        print(f"Created alerts for low stock items")
        
        print("\n=== SEEDING COMPLETE ===")
        print(f"Users: 3 (admin, manager, viewer)")
        print(f"Suppliers: {len(suppliers)}")
        print(f"Products: {len(products)}")
        print(f"Customers: {len(customers)}")
        print(f"Batches: {len(batches)}")
        print(f"Competitors: {len(competitors)}")
        print(f"Sales: 90 days of transactions")
        print(f"Alerts: Created for low stock items")
        print("\nLogin credentials:")
        print("  admin/password123")
        print("  manager/password123")
        print("  viewer/password123")

if __name__ == '__main__':
    seed_full_data()
