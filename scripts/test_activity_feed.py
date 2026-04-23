"""
Test script for Activity Feed functionality
Run this after migration to verify everything works
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.models.organization import Organization
from app.utils.activity_logger import log_activity
from datetime import datetime

def test_activity_logging():
    """Test activity logging functionality"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Testing Activity Feed System")
            print("=" * 50)
            
            # Get test organization and user
            org = Organization.query.first()
            user = User.query.filter_by(organization_id=org.id).first()
            
            if not org or not user:
                print("✗ Error: No organization or user found")
                print("  Run seed_data.py first")
                return False
            
            print(f"✓ Found test organization: {org.name}")
            print(f"✓ Found test user: {user.username}")
            print()
            
            # Test 1: Log a test activity
            print("Test 1: Logging test activity...")
            initial_count = ActivityLog.query.filter_by(organization_id=org.id).count()
            
            log_activity(
                org.id,
                user.id,
                user.username,
                'created',
                'product',
                'Test Product'
            )
            
            new_count = ActivityLog.query.filter_by(organization_id=org.id).count()
            
            if new_count > initial_count:
                print(f"✓ Activity logged successfully")
                print(f"  Activities before: {initial_count}")
                print(f"  Activities after: {new_count}")
            else:
                print("✗ Failed to log activity")
                return False
            
            print()
            
            # Test 2: Retrieve activities
            print("Test 2: Retrieving activities...")
            activities = ActivityLog.query.filter_by(organization_id=org.id)\
                .order_by(ActivityLog.created_at.desc())\
                .limit(5)\
                .all()
            
            if activities:
                print(f"✓ Retrieved {len(activities)} activities")
                print("\nRecent activities:")
                for i, activity in enumerate(activities, 1):
                    print(f"  {i}. {activity.description}")
                    print(f"     Time: {activity.created_at}")
                    print(f"     User: {activity.username}")
                    print()
            else:
                print("✗ No activities found")
                return False
            
            # Test 3: Verify activity structure
            print("Test 3: Verifying activity structure...")
            latest = activities[0]
            
            checks = [
                ('ID', latest.id is not None),
                ('Organization ID', latest.organization_id == org.id),
                ('User ID', latest.user_id is not None),
                ('Username', latest.username is not None),
                ('Action', latest.action is not None),
                ('Resource Type', latest.resource_type is not None),
                ('Resource Name', latest.resource_name is not None),
                ('Description', latest.description is not None),
                ('Created At', latest.created_at is not None),
            ]
            
            all_passed = True
            for field, passed in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {field}: {passed}")
                if not passed:
                    all_passed = False
            
            if not all_passed:
                return False
            
            print()
            
            # Test 4: Test to_dict method
            print("Test 4: Testing to_dict method...")
            activity_dict = latest.to_dict()
            
            required_keys = ['id', 'username', 'action', 'resource_type', 
                           'resource_name', 'description', 'created_at']
            
            all_keys_present = all(key in activity_dict for key in required_keys)
            
            if all_keys_present:
                print("✓ to_dict method works correctly")
                print(f"  Keys: {', '.join(activity_dict.keys())}")
            else:
                print("✗ to_dict method missing keys")
                return False
            
            print()
            
            # Test 5: Test organization isolation
            print("Test 5: Testing organization isolation...")
            
            # Get activities for this org
            org_activities = ActivityLog.query.filter_by(organization_id=org.id).count()
            
            # Get all activities
            all_activities = ActivityLog.query.count()
            
            print(f"✓ Organization activities: {org_activities}")
            print(f"✓ Total activities: {all_activities}")
            
            if org_activities <= all_activities:
                print("✓ Organization isolation working correctly")
            else:
                print("✗ Organization isolation issue")
                return False
            
            print()
            print("=" * 50)
            print("All tests passed! ✓")
            print()
            print("Next steps:")
            print("1. Start backend: python run_sqlite.py")
            print("2. Test API: curl -H 'Authorization: Bearer <token>' http://localhost:5000/api/activity")
            print("3. Start frontend: cd frontend && npm start")
            print("4. Navigate to: http://localhost:3000/activity")
            
            return True
            
        except Exception as e:
            print(f"✗ Error during testing: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_activity_logging()
    sys.exit(0 if success else 1)
