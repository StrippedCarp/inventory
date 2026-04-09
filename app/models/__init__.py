from app import db
from datetime import datetime

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    expected_delivery = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'supplier_id': self.supplier_id,
            'quantity_ordered': self.quantity_ordered,
            'order_date': self.order_date.isoformat(),
            'expected_delivery': self.expected_delivery.isoformat() if self.expected_delivery else None,
            'status': self.status
        }

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    predicted_demand = db.Column(db.Integer, nullable=False)
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'forecast_date': self.forecast_date.isoformat(),
            'predicted_demand': self.predicted_demand,
            'confidence_score': self.confidence_score
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }