"""
Migration script to add organization_id to competitors table
Run this to add organization isolation to competitors
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from sqlalchemy import text

def add_organization_to_competitors():
    """Add organization_id column to competitors table"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        try:
            print("Adding organization_id to competitors table...")
            
            # Add organization_id column
            db.session.execute(text("""
                ALTER TABLE competitors 
                ADD COLUMN organization_id INTEGER 
                REFERENCES organizations(id)
            """))
            
            # Set default organization (id=1) for existing competitors
            db.session.execute(text("""
                UPDATE competitors 
                SET organization_id = 1 
                WHERE organization_id IS NULL
            """))
            
            db.session.commit()
            
            print("✓ Successfully added organization_id to competitors table")
            print("✓ Existing competitors assigned to default organization (id=1)")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("Migrating competitors table to support organizations...")
    print("-" * 50)
    
    success = add_organization_to_competitors()
    
    print("-" * 50)
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
