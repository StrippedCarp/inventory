from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app import db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.utils.auth_decorators import admin_required, manager_or_admin_required
from app.utils.organization_context import get_organization_id, get_user_id
from app.utils.activity_logger import log_activity
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products for current organization"""
    try:
        org_id = get_organization_id()
        
        products = Product.query.filter_by(organization_id=org_id).all()
        
        result = {
            'products': [product.to_dict() for product in products],
            'total': len(products)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """Get single product by ID"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify(product.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    """Create new product for current organization"""
    try:
        org_id = get_organization_id()
        user_id = get_user_id()
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Validation error', 'message': 'No data provided'}), 400
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Validation error', 'message': 'Product name is required'}), 400
        
        if not data.get('unit_price'):
            return jsonify({'error': 'Validation error', 'message': 'Price is required'}), 400
        
        # Validate price is positive
        try:
            price = float(data['unit_price'])
            if price <= 0:
                return jsonify({'error': 'Validation error', 'message': 'Price must be a positive number'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Validation error', 'message': 'Price must be a valid number'}), 400
        
        # Validate other required fields
        required_fields = ['sku', 'category']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({'error': 'Validation error', 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Check if SKU already exists in organization
        if Product.query.filter_by(sku=data['sku'], organization_id=org_id).first():
            return jsonify({'message': 'SKU already exists'}), 409
        
        # Handle supplier_id - use first available supplier for this org if not provided
        supplier_id = data.get('supplier_id')
        if supplier_id:
            supplier = Supplier.query.filter_by(id=supplier_id, organization_id=org_id).first()
            if not supplier:
                return jsonify({'message': 'Supplier not found'}), 404
        else:
            # Use first available supplier for this org as default
            supplier = Supplier.query.filter_by(organization_id=org_id).first()
            if not supplier:
                return jsonify({'message': 'No suppliers available. Please create a supplier first.'}), 400
            supplier_id = supplier.id
        
        # Create product
        product = Product(
            sku=data['sku'],
            name=data['name'],
            category=data['category'],
            unit_price=float(data['unit_price']),
            description=data.get('description', ''),
            supplier_id=supplier_id,
            user_id=user_id,
            organization_id=org_id,
            reorder_point=int(data.get('reorder_point', 10)),
            safety_stock=int(data.get('safety_stock', 5))
        )
        
        db.session.add(product)
        db.session.flush()  # Get product ID before committing
        
        # Automatically create inventory record with 0 stock
        from app.models.inventory import Inventory
        inventory = Inventory(
            product_id=product.id,
            quantity_on_hand=0,
            warehouse_location='Main'
        )
        db.session.add(inventory)
        db.session.commit()
        
        # Log activity
        user = User.query.get(user_id)
        if user:
            log_activity(org_id, user_id, user.username, 'created', 'product', product.name)
        
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@manager_or_admin_required
def update_product(product_id):
    """Update product (Manager/Admin only)"""
    try:
        org_id = get_organization_id()
        
        product = Product.query.filter_by(id=product_id, organization_id=org_id).first()
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        updatable_fields = ['name', 'category', 'unit_price', 'description', 
                          'supplier_id', 'reorder_point', 'safety_stock']
        
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        # Verify supplier if being updated
        if 'supplier_id' in data:
            supplier = Supplier.query.filter_by(id=data['supplier_id'], organization_id=org_id).first()
            if not supplier:
                return jsonify({'message': 'Supplier not found'}), 404
        
        db.session.commit()
        
        # Log activity
        user_id = get_user_id()
        user = User.query.get(user_id)
        if user:
            log_activity(org_id, user_id, user.username, 'updated', 'product', product.name)
        
        return jsonify(product.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete product (Admin only)"""
    try:
        org_id = get_organization_id()
        
        product = Product.query.filter_by(id=product_id, organization_id=org_id).first()
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        
        # Log activity
        user_id = get_user_id()
        user = User.query.get(user_id)
        if user:
            log_activity(org_id, user_id, user.username, 'deleted', 'product', product_name)
        
        return jsonify({'message': 'Product deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/debug', methods=['GET'])
def debug_products_get():
    """Debug route to check database and models (GET only)"""
    try:
        # Check database tables
        suppliers = Supplier.query.all()
        products = Product.query.all()
        
        return jsonify({
            'suppliers_count': len(suppliers),
            'products_count': len(products),
            'suppliers': [{'id': s.id, 'name': s.name} for s in suppliers[:3]],
            'products': [{'id': p.id, 'name': p.name} for p in products[:3]]
        })
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'db_session': str(db.session)
        }), 500

@products_bp.route('/debug', methods=['POST'])
def debug_products_post():
    """Debug route for POST testing"""
    try:
        # Try minimal product creation
        data = request.get_json() or {}
        
        return jsonify({
            'received_data': data,
            'db_connected': db.session is not None,
            'can_query': bool(Supplier.query.first())
        })
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'type': type(e).__name__,
            'db_session': str(db.session)
        }), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [cat[0] for cat in categories]
        
        return jsonify({'categories': category_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500