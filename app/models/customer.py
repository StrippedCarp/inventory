from app import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    customer_type = db.Column(db.String(20), default='regular')  # regular, vip, wholesale
    loyalty_points = db.Column(db.Integer, default=0)
    total_purchases = db.Column(db.Float, default=0.0)
    discount_percentage = db.Column(db.Float, default=0.0)  # Customer-specific discount
    credit_limit = db.Column(db.Float, default=0.0)
    outstanding_balance = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'customer_type': self.customer_type,
            'loyalty_points': self.loyalty_points,
            'total_purchases': self.total_purchases,
            'discount_percentage': self.discount_percentage,
            'credit_limit': self.credit_limit,
            'outstanding_balance': self.outstanding_balance,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CustomerPricing(db.Model):
    __tablename__ = 'customer_pricing'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    special_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='special_prices')
    product = db.relationship('Product', backref='customer_prices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'special_price': self.special_price,
            'created_at': self.created_at.isoformat()
        }

class LoyaltyTransaction(db.Model):
    __tablename__ = 'loyalty_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # positive for earned, negative for redeemed
    transaction_type = db.Column(db.String(20), nullable=False)  # earned, redeemed, adjusted
    reference_id = db.Column(db.Integer, nullable=True)  # sales_transaction_id
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='loyalty_transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'points': self.points,
            'transaction_type': self.transaction_type,
            'reference_id': self.reference_id,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
