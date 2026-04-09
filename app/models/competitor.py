from app import db
from datetime import datetime

class Competitor(db.Model):
    __tablename__ = 'competitors'
    
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sales_data = db.relationship('CompetitorSales', backref='competitor', lazy=True, cascade='all, delete-orphan')
    products = db.relationship('CompetitorProduct', backref='competitor', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
            'owner_name': self.owner_name,
            'category': self.category,
            'location': self.location,
            'phone': self.phone,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class CompetitorSales(db.Model):
    __tablename__ = 'competitor_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    daily_sales = db.Column(db.Numeric(10, 2))
    monthly_sales = db.Column(db.Numeric(10, 2))
    yearly_sales = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'competitor_id': self.competitor_id,
            'date': self.date.isoformat(),
            'daily_sales': float(self.daily_sales) if self.daily_sales else 0,
            'monthly_sales': float(self.monthly_sales) if self.monthly_sales else 0,
            'yearly_sales': float(self.yearly_sales) if self.yearly_sales else 0
        }

class CompetitorProduct(db.Model):
    __tablename__ = 'competitor_products'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'competitor_id': self.competitor_id,
            'product_name': self.product_name,
            'category': self.category,
            'price': float(self.price)
        }
