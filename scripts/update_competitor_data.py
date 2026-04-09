"""
Script to update competitor sales data
Run this weekly/monthly to keep competitor data current
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.competitor import Competitor, CompetitorSales, CompetitorProduct
from datetime import date, timedelta
import random

def update_competitor_sales():
    """Update sales data for all competitors"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        competitors = Competitor.query.all()
        
        if not competitors:
            print("No competitors found. Add competitors first.")
            return
        
        today = date.today()
        
        for competitor in competitors:
            # Generate realistic sales based on category
            if competitor.category == 'grocery':
                daily_base = random.randint(10000, 50000)
            elif competitor.category == 'electronics':
                daily_base = random.randint(15000, 80000)
            elif competitor.category == 'clothing':
                daily_base = random.randint(8000, 40000)
            else:
                daily_base = random.randint(5000, 30000)
            
            # Add some variance
            daily_sales = daily_base * random.uniform(0.8, 1.2)
            monthly_sales = daily_sales * 30 * random.uniform(0.9, 1.1)
            yearly_sales = monthly_sales * 12 * random.uniform(0.95, 1.05)
            
            # Check if sales record exists for today
            existing = CompetitorSales.query.filter_by(
                competitor_id=competitor.id,
                date=today
            ).first()
            
            if existing:
                # Update existing record
                existing.daily_sales = daily_sales
                existing.monthly_sales = monthly_sales
                existing.yearly_sales = yearly_sales
                print(f"Updated sales for {competitor.business_name}")
            else:
                # Create new record
                sales = CompetitorSales(
                    competitor_id=competitor.id,
                    date=today,
                    daily_sales=daily_sales,
                    monthly_sales=monthly_sales,
                    yearly_sales=yearly_sales
                )
                db.session.add(sales)
                print(f"Added sales data for {competitor.business_name}")
        
        db.session.commit()
        print(f"\nSales data updated for {len(competitors)} competitors")

def update_competitor_prices():
    """Update product prices for competitors"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        products = CompetitorProduct.query.all()
        
        if not products:
            print("No competitor products found.")
            return
        
        updated = 0
        for product in products:
            # Simulate price changes (±5%)
            if random.random() < 0.3:  # 30% chance of price change
                old_price = float(product.price)
                change = random.uniform(-0.05, 0.05)
                new_price = old_price * (1 + change)
                product.price = round(new_price, 2)
                updated += 1
                print(f"Updated {product.product_name}: KES {old_price:.2f} → KES {new_price:.2f}")
        
        db.session.commit()
        print(f"\nUpdated prices for {updated} products")

def generate_historical_data(days=30):
    """Generate historical sales data for competitors"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        competitors = Competitor.query.all()
        
        if not competitors:
            print("No competitors found.")
            return
        
        start_date = date.today() - timedelta(days=days)
        
        for competitor in competitors:
            print(f"Generating {days} days of data for {competitor.business_name}...")
            
            current_date = start_date
            while current_date <= date.today():
                # Check if data already exists
                existing = CompetitorSales.query.filter_by(
                    competitor_id=competitor.id,
                    date=current_date
                ).first()
                
                if not existing:
                    # Generate sales data
                    if competitor.category == 'grocery':
                        daily_base = random.randint(10000, 50000)
                    elif competitor.category == 'electronics':
                        daily_base = random.randint(15000, 80000)
                    else:
                        daily_base = random.randint(5000, 30000)
                    
                    daily_sales = daily_base * random.uniform(0.8, 1.2)
                    monthly_sales = daily_sales * 30 * random.uniform(0.9, 1.1)
                    yearly_sales = monthly_sales * 12 * random.uniform(0.95, 1.05)
                    
                    sales = CompetitorSales(
                        competitor_id=competitor.id,
                        date=current_date,
                        daily_sales=daily_sales,
                        monthly_sales=monthly_sales,
                        yearly_sales=yearly_sales
                    )
                    db.session.add(sales)
                
                current_date += timedelta(days=1)
            
            db.session.commit()
        
        print(f"\nHistorical data generated for {len(competitors)} competitors")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Update competitor data')
    parser.add_argument('--sales', action='store_true', help='Update sales data')
    parser.add_argument('--prices', action='store_true', help='Update product prices')
    parser.add_argument('--historical', type=int, metavar='DAYS', help='Generate historical data')
    
    args = parser.parse_args()
    
    if args.sales:
        update_competitor_sales()
    elif args.prices:
        update_competitor_prices()
    elif args.historical:
        generate_historical_data(args.historical)
    else:
        print("Usage:")
        print("  python scripts/update_competitor_data.py --sales       # Update today's sales")
        print("  python scripts/update_competitor_data.py --prices      # Update product prices")
        print("  python scripts/update_competitor_data.py --historical 30  # Generate 30 days of data")
