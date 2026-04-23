"""
Migration script to add activity_logs table
Run this script to add activity logging to existing database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.activity_log import ActivityLog

def add_activity_logs_table():
    """Add activity_logs table to database"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        try:
            # Create activity_logs table
            db.create_all()
            print("✓ Activity logs table created successfully")
            
            # Verify table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'activity_logs' in tables:
                print("✓ Verified: activity_logs table exists")
                print("\nTable columns:")
                columns = inspector.get_columns('activity_logs')
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("✗ Error: activity_logs table not found")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Error creating activity_logs table: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Adding activity_logs table to database...")
    print("-" * 50)
    
    success = add_activity_logs_table()
    
    print("-" * 50)
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
