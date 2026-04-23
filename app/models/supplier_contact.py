from app import db
from datetime import datetime

class SupplierContact(db.Model):
    __tablename__ = 'supplier_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    contact_method = db.Column(db.String(20), nullable=False)  # 'email' or 'sms'
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='supplier_contacts')
    supplier = db.relationship('Supplier', backref='contact_requests')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'message': self.message,
            'contact_method': self.contact_method,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
