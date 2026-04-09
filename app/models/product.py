from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    reorder_point = db.Column(db.Integer, default=10)
    safety_stock = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventory = db.relationship('Inventory', backref='product', uselist=False)
    sales_transactions = db.relationship('SalesTransaction', backref='product', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='product', lazy=True)
    forecasts = db.relationship('Forecast', backref='product', lazy=True)
    alerts = db.relationship('Alert', backref='product', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'category': self.category,
            'unit_price': float(self.unit_price),
            'description': self.description,
            'supplier_id': self.supplier_id,
            'reorder_point': self.reorder_point,
            'safety_stock': self.safety_stock,
            'supplier_name': self.supplier.name if self.supplier else None
        }