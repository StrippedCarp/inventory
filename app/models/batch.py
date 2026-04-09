from app import db
from datetime import datetime

class Batch(db.Model):
    __tablename__ = 'batches'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False, unique=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    cost_per_unit = db.Column(db.Float, nullable=False)
    manufacture_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    received_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, expired, depleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='batches')
    supplier = db.relationship('Supplier', backref='batches')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'batch_number': self.batch_number,
            'quantity': self.quantity,
            'cost_per_unit': self.cost_per_unit,
            'manufacture_date': self.manufacture_date.isoformat() if self.manufacture_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'received_date': self.received_date.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class BatchTransaction(db.Model):
    __tablename__ = 'batch_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # sale, adjustment, return
    quantity = db.Column(db.Integer, nullable=False)
    reference_id = db.Column(db.Integer, nullable=True)  # sales_transaction_id or other reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    batch = db.relationship('Batch', backref='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'batch_number': self.batch.batch_number if self.batch else None,
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat()
        }
