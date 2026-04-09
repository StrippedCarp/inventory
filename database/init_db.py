"""Database Initialization Script"""
from backend.common.utils.db import db
from backend.inventory_service.app import app

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")

if __name__ == '__main__':
    init_db()
