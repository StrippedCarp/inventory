from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import HTTPException
import os
import traceback

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
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 2592000  # 30 days
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Token expired: {jwt_payload}")
        return {'message': 'Token has expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token: {error}")
        return {'message': 'Invalid token'}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        print(f"Unauthorized: {error}")
        return {'message': 'Missing authorization token'}, 401
    
    # Import models to ensure they're registered
    from app.models.user import User
    from app.models.supplier import Supplier
    from app.models.supplier_contact import SupplierContact
    from app.models.customer_contact import CustomerContact
    from app.models.product import Product
    from app.models.inventory import Inventory
    from app.models.sales_transaction import SalesTransaction
    from app.models.competitor import Competitor, CompetitorSales, CompetitorProduct
    from app.models.customer import Customer, CustomerPricing, LoyaltyTransaction
    from app.models.batch import Batch, BatchTransaction
    from app.models.invitation import Invitation
    from app.models.activity_log import ActivityLog
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
    from app.routes.admin import admin_bp
    from app.routes.invitations import invitations_bp
    from app.routes.organizations import organizations_bp
    from app.routes.activity import activity_bp
    
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
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(invitations_bp, url_prefix='/api/invitations')
    app.register_blueprint(organizations_bp, url_prefix='/api/organizations')
    app.register_blueprint(activity_bp, url_prefix='/api/activity')
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Inventory Management API is running'}
    
    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'error': 'Bad request',
            'message': str(e.description) if hasattr(e, 'description') else 'Invalid request data'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Please login again'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            'error': 'Forbidden',
            'message': "You don't have permission to do this"
        }), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource does not exist'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        print(f"Internal server error: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': 'Something went wrong, please try again'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e
        
        # Log the error
        print(f"Unhandled exception: {str(e)}")
        print(traceback.format_exc())
        
        # Return generic error
        return jsonify({
            'error': 'Server error',
            'message': 'Something went wrong, please try again'
        }), 500
    
    return app