from app import db
from datetime import datetime

class CustomerContact(db.Model):
    __tablename__ = 'customer_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    contact_method = db.Column(db.String(20), nullable=False)  # 'email' or 'sms'
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='customer_contacts')
    customer = db.relationship('Customer', backref='contact_requests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'message': self.message,
            'contact_method': self.contact_method,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
