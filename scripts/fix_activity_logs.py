"""
Fix NULL user_id values in activity_logs table
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.activity_log import ActivityLog
from app.models.user import User

def fix_activity_logs():
    """Fix NULL user_id values in activity_logs"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        try:
            print("Fixing activity logs with NULL user_id...")
            print("-" * 50)
            
            # Find activities with NULL user_id
            null_activities = ActivityLog.query.filter(ActivityLog.user_id == None).all()
            
            if not null_activities:
                print("✓ No activities with NULL user_id found")
                return True
            
            print(f"Found {len(null_activities)} activities with NULL user_id")
            
            # For each activity, try to find a user in the same organization
            fixed_count = 0
            deleted_count = 0
            
            for activity in null_activities:
                # Try to find any user in the same organization
                user = User.query.filter_by(organization_id=activity.organization_id).first()
                
                if user:
                    # Assign to first available user in organization
                    activity.user_id = user.id
                    activity.username = user.username
                    fixed_count += 1
                    print(f"  ✓ Fixed activity {activity.id}: assigned to {user.username}")
                else:
                    # No users in organization, delete the activity
                    db.session.delete(activity)
                    deleted_count += 1
                    print(f"  ✗ Deleted activity {activity.id}: no users in organization")
            
            db.session.commit()
            
            print()
            print("-" * 50)
            print(f"✓ Fixed {fixed_count} activities")
            print(f"✓ Deleted {deleted_count} orphaned activities")
            print("Activity logs cleaned successfully!")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Fixing Activity Logs")
    print("=" * 50)
    
    success = fix_activity_logs()
    
    print("=" * 50)
    if success:
        print("Fix completed successfully!")
    else:
        print("Fix failed!")
        sys.exit(1)
