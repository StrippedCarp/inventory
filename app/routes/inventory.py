from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sales_transaction import SalesTransaction
from app.models.user import User
from app.utils.auth_decorators import manager_or_admin_required
from app.utils.organization_context import get_organization_id, get_user_id
from app.utils.activity_logger import log_activity
from datetime import date

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/items', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get all inventory items with product details"""
    try:
        org_id = get_organization_id()
        low_stock_only = request.args.get('low_stock', 'false').lower() == 'true'
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = db.session.query(Inventory, Product).join(Product).filter(Product.organization_id == org_id)
        
        # Apply filters
        if low_stock_only:
            query = query.filter(Inventory.quantity_on_hand <= Product.reorder_point)
        
        if category:
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        
        inventory_items = query.all()
        
        result = []
        for inventory, product in inventory_items:
            item_data = {
                'item_id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category,
                'current_stock': inventory.quantity_on_hand,
                'reorder_level': product.reorder_point,
                'safety_stock': product.safety_stock,
                'unit_price': float(product.unit_price),
                'location': inventory.warehouse_location,
                'last_updated': inventory.last_updated.isoformat(),
                'total_value': inventory.quantity_on_hand * float(product.unit_price),
                'status': get_stock_status(inventory.quantity_on_hand, product.reorder_point),
                'supplier_name': product.supplier.name if product.supplier else None
            }
            result.append(item_data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product_inventory(product_id):
    """Get inventory for specific product"""
    try:
        inventory = db.session.query(Inventory, Product).join(Product).filter(
            Inventory.product_id == product_id
        ).first()
        
        if not inventory:
            return jsonify({'message': 'Inventory not found'}), 404
        
        inv, product = inventory
        result = {
            **inv.to_dict(),
            'product_name': product.name,
            'sku': product.sku,
            'category': product.category,
            'unit_price': float(product.unit_price),
            'reorder_point': product.reorder_point,
            'safety_stock': product.safety_stock,
            'status': get_stock_status(inv.quantity_on_hand, product.reorder_point)
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:product_id>/adjust', methods=['POST'])
@jwt_required()
def adjust_inventory(product_id):
    """Adjust inventory quantity with reason tracking"""
    try:
        org_id = get_organization_id()
        data = request.get_json()
        adjustment_type = data.get('type')  # 'add', 'remove', 'set'
        quantity = data.get('quantity')
        reason = data.get('reason', 'Manual adjustment')
        
        if not adjustment_type or quantity is None:
            return jsonify({'message': 'Type and quantity are required'}), 400
        
        inventory = db.session.query(Inventory).join(Product).filter(
            Inventory.product_id == product_id,
            Product.organization_id == org_id
        ).first()
        if not inventory:
            return jsonify({'message': 'Inventory not found'}), 404
        
        old_quantity = inventory.quantity_on_hand
        
        if adjustment_type == 'add':
            inventory.quantity_on_hand += quantity
        elif adjustment_type == 'remove':
            inventory.quantity_on_hand = max(0, inventory.quantity_on_hand - quantity)
        elif adjustment_type == 'set':
            inventory.quantity_on_hand = max(0, quantity)
        else:
            return jsonify({'message': 'Invalid adjustment type'}), 400
        
        db.session.commit()
        
        # Log activity
        user_id = get_user_id()
        user = User.query.get(user_id)
        product = Product.query.get(product_id)
        if user and product:
            log_activity(org_id, user_id, user.username, 'adjusted stock for', 'inventory', product.name)
        
        # Log the adjustment
        adjustment_log = {
            'product_id': product_id,
            'old_quantity': old_quantity,
            'new_quantity': inventory.quantity_on_hand,
            'adjustment': inventory.quantity_on_hand - old_quantity,
            'reason': reason,
            'user_id': 'system'
        }
        
        return jsonify({
            'message': 'Inventory adjusted successfully',
            'inventory': inventory.to_dict(),
            'adjustment_log': adjustment_log
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:product_id>/sale', methods=['POST'])
@jwt_required()
def record_sale(product_id):
    """Record a sale and update inventory"""
    try:
        org_id = get_organization_id()
        data = request.get_json()
        quantity_sold = data.get('quantity_sold')
        unit_price = data.get('unit_price')
        
        if not quantity_sold or not unit_price:
            return jsonify({'message': 'Quantity and unit price are required'}), 400
        
        # Check inventory availability
        inventory = db.session.query(Inventory).join(Product).filter(
            Inventory.product_id == product_id,
            Product.organization_id == org_id
        ).first()
        if not inventory:
            return jsonify({'message': 'Product not found in inventory'}), 404
        
        if inventory.quantity_on_hand < quantity_sold:
            return jsonify({
                'message': f'Insufficient stock. Available: {inventory.quantity_on_hand}'
            }), 400
        
        # Create sales transaction
        sale = SalesTransaction(
            product_id=product_id,
            quantity_sold=quantity_sold,
            sale_date=date.today(),
            unit_price=unit_price,
            total_amount=quantity_sold * unit_price
        )
        
        # Update inventory
        inventory.quantity_on_hand -= quantity_sold
        
        db.session.add(sale)
        db.session.commit()
        
        return jsonify({
            'message': 'Sale recorded successfully',
            'sale': sale.to_dict(),
            'remaining_stock': inventory.quantity_on_hand
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock():
    """Get items with low stock levels"""
    try:
        org_id = get_organization_id()
        low_stock_items = db.session.query(Inventory, Product).join(Product).filter(
            Product.organization_id == org_id,
            Inventory.quantity_on_hand <= Product.reorder_point
        ).all()
        
        result = []
        for inventory, product in low_stock_items:
            item_data = {
                'item_id': product.id,
                'name': product.name,
                'sku': product.sku,
                'current_stock': inventory.quantity_on_hand,
                'reorder_level': product.reorder_point,
                'safety_stock': product.safety_stock,
                'unit_price': float(product.unit_price),
                'shortage': product.reorder_point - inventory.quantity_on_hand,
                'status': 'critical' if inventory.quantity_on_hand == 0 else 'low',
                'supplier_name': product.supplier.name if product.supplier else None
            }
            result.append(item_data)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_inventory_summary():
    """Get inventory summary statistics for current organization"""
    try:
        org_id = get_organization_id()
        
        total_products = db.session.query(Product).filter_by(organization_id=org_id).count()
        
        low_stock_count = db.session.query(Inventory).join(Product).filter(
            Product.organization_id == org_id,
            Inventory.quantity_on_hand <= Product.reorder_point
        ).count()
        
        out_of_stock_count = db.session.query(Inventory).join(Product).filter(
            Product.organization_id == org_id,
            Inventory.quantity_on_hand == 0
        ).count()
        
        total_value = db.session.query(
            db.func.sum(Inventory.quantity_on_hand * Product.unit_price)
        ).join(Product).filter(Product.organization_id == org_id).scalar() or 0
        
        return jsonify({
            'total_products': total_products,
            'low_stock_items': low_stock_count,
            'out_of_stock_items': out_of_stock_count,
            'total_inventory_value': float(total_value)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items', methods=['POST'])
@manager_or_admin_required
def create_inventory_item():
    """Create new inventory item"""
    try:
        data = request.get_json()
        
        # Check if product exists
        product = Product.query.get(data.get('product_id'))
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Check if inventory already exists
        existing = Inventory.query.filter_by(product_id=data.get('product_id')).first()
        if existing:
            return jsonify({'message': 'Inventory for this product already exists'}), 400
        
        inventory = Inventory(
            product_id=data.get('product_id'),
            quantity_on_hand=data.get('quantity_on_hand', 0),
            warehouse_location=data.get('warehouse_location', 'Main')
        )
        
        db.session.add(inventory)
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item created successfully',
            'inventory': inventory.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:product_id>', methods=['PUT'])
@manager_or_admin_required
def update_inventory_item(product_id):
    """Update inventory item"""
    try:
        org_id = get_organization_id()
        data = request.get_json()
        
        inventory = db.session.query(Inventory).join(Product).filter(
            Inventory.product_id == product_id,
            Product.organization_id == org_id
        ).first()
        if not inventory:
            return jsonify({'message': 'Inventory not found'}), 404
        
        # Update fields
        if 'quantity_on_hand' in data:
            inventory.quantity_on_hand = data['quantity_on_hand']
        if 'warehouse_location' in data:
            inventory.warehouse_location = data['warehouse_location']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory updated successfully',
            'inventory': inventory.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@inventory_bp.route('/items/<int:product_id>', methods=['DELETE'])
@manager_or_admin_required
def delete_inventory_item(product_id):
    """Delete inventory item"""
    try:
        org_id = get_organization_id()
        inventory = db.session.query(Inventory).join(Product).filter(
            Inventory.product_id == product_id,
            Product.organization_id == org_id
        ).first()
        if not inventory:
            return jsonify({'message': 'Inventory not found'}), 404
        
        db.session.delete(inventory)
        db.session.commit()
        
        return jsonify({'message': 'Inventory item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_stock_status(current_stock, reorder_point):
    """Helper function to determine stock status"""
    if current_stock == 0:
        return 'out_of_stock'
    elif current_stock <= reorder_point:
        return 'low_stock'
    else:
        return 'in_stock'