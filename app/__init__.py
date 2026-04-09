from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
jwt = JWTManager()

def create_app(use_sqlite=False):
    app = Flask(__name__)
    
    # Configuration from environment variables
    if use_sqlite:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://inventory_user:inventory_pass@localhost:5432/inventory_db')
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return {'message': 'Missing authorization token'}, 401
    
    # Import models to ensure they're registered
    from app.models.user import User
    from app.models.supplier import Supplier
    from app.models.supplier_contact import SupplierContact
    from app.models.product import Product
    from app.models.inventory import Inventory
    from app.models.sales_transaction import SalesTransaction
    from app.models.competitor import Competitor, CompetitorSales, CompetitorProduct
    from app.models.customer import Customer, CustomerPricing, LoyaltyTransaction
    from app.models.batch import Batch, BatchTransaction
    from app.models import PurchaseOrder, Forecast, Alert
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.competitors import competitors_bp
    from app.routes.admin_competitors import admin_competitors_bp
    from app.routes.inventory import inventory_bp
    from app.routes.sales import sales_bp
    from app.routes.alerts import alerts_bp
    from app.routes.forecast import forecast_bp
    from app.routes.orders import orders_bp
    from app.routes.analytics import analytics_bp
    from app.routes.users import users_bp
    from app.routes.customers import customers_bp
    from app.routes.batches import batches_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(suppliers_bp, url_prefix='/api/suppliers')
    app.register_blueprint(competitors_bp, url_prefix='/api/competitors')
    app.register_blueprint(admin_competitors_bp, url_prefix='/api/admin/competitors')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(forecast_bp, url_prefix='/api/forecast')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(batches_bp, url_prefix='/api/batches')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Inventory Management API is running'}
    
    return app