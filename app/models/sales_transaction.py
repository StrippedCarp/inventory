from app import db
from datetime import datetime

class SalesTransaction(db.Model):
    __tablename__ = 'sales_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    discount_applied = db.Column(db.Numeric(10, 2), default=0)
    loyalty_points_earned = db.Column(db.Integer, default=0)
    loyalty_points_redeemed = db.Column(db.Integer, default=0)
    payment_method = db.Column(db.String(20), default='cash')  # cash, card, credit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'customer_id': self.customer_id,
            'quantity_sold': self.quantity_sold,
            'sale_date': self.sale_date.isoformat(),
            'unit_price': float(self.unit_price),
            'total_amount': float(self.total_amount),
            'discount_applied': float(self.discount_applied),
            'loyalty_points_earned': self.loyalty_points_earned,
            'loyalty_points_redeemed': self.loyalty_points_redeemed,
            'payment_method': self.payment_method,
            'product_name': self.product.name if self.product else None,
            'customer_name': self.customer.name if self.customer else None
        }