#!/usr/bin/env python3
"""SQLite Database initialization script"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

def init_sqlite_database():
    """Initialize SQLite database with tables"""
    app = create_app(use_sqlite=True)
    
    with app.app_context():
        print("Creating SQLite database tables...")
        
        # Create all tables
        db.create_all()
        
        print("SQLite database tables created successfully!")
        print("Database file: inventory.db")

if __name__ == '__main__':
    init_sqlite_database()