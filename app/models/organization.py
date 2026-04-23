from app import db
from datetime import datetime

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    subscription_plan = db.Column(db.String(50), default='free')  # free, basic, premium
    subscription_status = db.Column(db.String(20), default='active')  # active, suspended, cancelled
    max_users = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'max_users': self.max_users,
            'user_count': len(self.users),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
