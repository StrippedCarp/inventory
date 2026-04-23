"""
Seed script for activity logs
Creates sample activity data for testing the activity feed
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.models.organization import Organization
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from datetime import datetime, timedelta
import random

def seed_activities():
    """Seed activity logs with sample data"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        try:
            print("Seeding activity logs...")
            print("-" * 50)
            
            # Get organizations
            orgs = Organization.query.all()
            if not orgs:
                print("✗ No organizations found. Run seed_data.py first.")
                return False
            
            activities_created = 0
            
            for org in orgs:
                print(f"\nSeeding activities for organization: {org.name}")
                
                # Get users in this organization
                users = User.query.filter_by(organization_id=org.id).all()
                if not users:
                    print(f"  ✗ No users found in {org.name}")
                    continue
                
                # Get resources for this organization
                products = Product.query.filter_by(organization_id=org.id).all()
                customers = Customer.query.filter_by(organization_id=org.id).all()
                suppliers = Supplier.query.filter_by(organization_id=org.id).all()
                
                # Define activity templates
                activity_templates = []
                
                # Product activities
                for product in products[:5]:  # Limit to first 5 products
                    activity_templates.extend([
                        ('created', 'product', product.name),
                        ('updated', 'product', product.name),
                    ])
                
                # Customer activities
                for customer in customers[:3]:  # Limit to first 3 customers
                    activity_templates.extend([
                        ('created', 'customer', customer.name),
                        ('updated', 'customer', customer.name),
                    ])
                
                # Supplier activities
                for supplier in suppliers[:3]:  # Limit to first 3 suppliers
                    activity_templates.extend([
                        ('created', 'supplier', supplier.name),
                        ('updated', 'supplier', supplier.name),
                    ])
                
                # Inventory activities
                for product in products[:3]:
                    activity_templates.append(('adjusted stock for', 'inventory', product.name))
                
                # Organization activities
                activity_templates.extend([
                    ('updated', 'organization settings', org.name),
                    ('sent invitation to', 'user', 'newuser@example.com'),
                    ('changed role to manager for', 'member', users[0].username if users else 'user'),
                ])
                
                # Create activities with varying timestamps
                now = datetime.utcnow()
                
                for i, (action, resource_type, resource_name) in enumerate(activity_templates):
                    # Distribute activities over the last 7 days
                    days_ago = random.randint(0, 7)
                    hours_ago = random.randint(0, 23)
                    minutes_ago = random.randint(0, 59)
                    
                    created_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                    
                    # Pick a random user from this organization
                    user = random.choice(users)
                    
                    # Build description
                    description = f"{user.username} {action} {resource_type} {resource_name}"
                    
                    activity = ActivityLog(
                        organization_id=org.id,
                        user_id=user.id,
                        username=user.username,
                        action=action,
                        resource_type=resource_type,
                        resource_name=resource_name,
                        description=description,
                        created_at=created_at
                    )
                    
                    db.session.add(activity)
                    activities_created += 1
                
                print(f"  ✓ Created {len(activity_templates)} activities for {org.name}")
            
            db.session.commit()
            
            print()
            print("-" * 50)
            print(f"✓ Successfully created {activities_created} activity logs")
            print()
            print("Activity breakdown by action:")
            
            # Show breakdown
            actions = db.session.query(
                ActivityLog.action,
                db.func.count(ActivityLog.id)
            ).group_by(ActivityLog.action).all()
            
            for action, count in actions:
                print(f"  - {action}: {count}")
            
            print()
            print("Recent activities:")
            recent = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
            for activity in recent:
                print(f"  - {activity.description}")
                print(f"    ({activity.created_at.strftime('%Y-%m-%d %H:%M:%S')})")
            
            return True
            
        except Exception as e:
            print(f"✗ Error seeding activities: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Seeding Activity Logs")
    print("=" * 50)
    
    success = seed_activities()
    
    print("=" * 50)
    if success:
        print("Seeding completed successfully!")
        print()
        print("Next steps:")
        print("1. Start backend: python run_sqlite.py")
        print("2. Start frontend: cd frontend && npm start")
        print("3. Navigate to: http://localhost:3000/activity")
    else:
        print("Seeding failed!")
        sys.exit(1)
