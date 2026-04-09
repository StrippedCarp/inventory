from app import db
from datetime import datetime

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, unique=True)
    quantity_on_hand = db.Column(db.Integer, nullable=False, default=0)
    warehouse_location = db.Column(db.String(20))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity_on_hand': self.quantity_on_hand,
            'warehouse_location': self.warehouse_location,
            'last_updated': self.last_updated.isoformat(),
            'product_name': self.product.name if self.product else None,
            'unit_price': float(self.product.unit_price) if self.product else 0,
            'reorder_point': self.product.reorder_point if self.product else 0
        }