from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import PurchaseOrder
from app.models.product import Product
from app.models.supplier import Supplier
from app.utils.auth_decorators import admin_required, manager_or_admin_required
from datetime import datetime, date

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get purchase orders with filtering"""
    try:
        status = request.args.get('status')
        supplier_id = request.args.get('supplier_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = db.session.query(PurchaseOrder, Product, Supplier).join(
            Product
        ).join(Supplier)
        
        # Apply filters
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        
        # Paginate results
        orders = query.order_by(PurchaseOrder.order_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'orders': [
                {
                    **order.to_dict(),
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'supplier_name': supplier.name,
                    'total_value': order.quantity_ordered * float(product.unit_price)
                }
                for order, product, supplier in orders.items
            ],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get single purchase order"""
    try:
        order_data = db.session.query(PurchaseOrder, Product, Supplier).join(
            Product
        ).join(Supplier).filter(PurchaseOrder.id == order_id).first()
        
        if not order_data:
            return jsonify({'message': 'Order not found'}), 404
        
        order, product, supplier = order_data
        
        result = {
            **order.to_dict(),
            'product': product.to_dict(),
            'supplier': supplier.to_dict(),
            'total_value': order.quantity_ordered * float(product.unit_price)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('', methods=['POST'])
@manager_or_admin_required
def create_order():
    """Create new purchase order"""
    try:
        data = request.get_json()
        
        required_fields = ['product_id', 'supplier_id', 'quantity_ordered']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verify product and supplier exist
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        supplier = Supplier.query.get(data['supplier_id'])
        if not supplier:
            return jsonify({'message': 'Supplier not found'}), 404
        
        # Calculate expected delivery
        from datetime import timedelta
        expected_delivery = date.today() + timedelta(days=supplier.lead_time_days)
        
        # Create order
        order = PurchaseOrder(
            product_id=data['product_id'],
            supplier_id=data['supplier_id'],
            quantity_ordered=data['quantity_ordered'],
            order_date=date.today(),
            expected_delivery=expected_delivery,
            status='pending'
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify(order.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/approve', methods=['PUT'])
@manager_or_admin_required
def approve_order(order_id):
    """Approve a purchase order"""
    try:
        order = PurchaseOrder.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.status != 'pending_approval':
            return jsonify({'message': 'Order is not pending approval'}), 400
        
        order.status = 'pending'
        db.session.commit()
        
        return jsonify({
            'message': 'Order approved successfully',
            'order': order.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/receive', methods=['PUT'])
@manager_or_admin_required
def receive_order(order_id):
    """Mark order as received and update inventory"""
    try:
        data = request.get_json()
        quantity_received = data.get('quantity_received')
        
        if not quantity_received:
            return jsonify({'message': 'quantity_received is required'}), 400
        
        order = PurchaseOrder.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.status not in ['pending', 'shipped']:
            return jsonify({'message': 'Order cannot be received in current status'}), 400
        
        # Update inventory
        from app.models.inventory import Inventory
        inventory = Inventory.query.filter_by(product_id=order.product_id).first()
        
        if inventory:
            inventory.quantity_on_hand += quantity_received
        else:
            # Create inventory record if it doesn't exist
            inventory = Inventory(
                product_id=order.product_id,
                quantity_on_hand=quantity_received,
                warehouse_location='A1-A1'  # Default location
            )
            db.session.add(inventory)
        
        # Update order status
        order.status = 'received'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order received successfully',
            'order': order.to_dict(),
            'inventory_updated': True,
            'new_stock_level': inventory.quantity_on_hand
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@manager_or_admin_required
def cancel_order(order_id):
    """Cancel a purchase order"""
    try:
        data = request.get_json()
        reason = data.get('reason', 'Cancelled by user')
        
        order = PurchaseOrder.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.status in ['received', 'cancelled']:
            return jsonify({'message': 'Order cannot be cancelled in current status'}), 400
        
        order.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict(),
            'reason': reason
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_orders_summary():
    """Get purchase orders summary statistics"""
    try:
        # Count orders by status
        pending_count = PurchaseOrder.query.filter_by(status='pending').count()
        approval_count = PurchaseOrder.query.filter_by(status='pending_approval').count()
        shipped_count = PurchaseOrder.query.filter_by(status='shipped').count()
        
        # Calculate total values
        from sqlalchemy import func
        total_pending_value = db.session.query(
            func.sum(PurchaseOrder.quantity_ordered * Product.unit_price)
        ).join(Product).filter(PurchaseOrder.status == 'pending').scalar() or 0
        
        # Get overdue orders
        from datetime import date
        overdue_count = PurchaseOrder.query.filter(
            PurchaseOrder.expected_delivery < date.today(),
            PurchaseOrder.status.in_(['pending', 'shipped'])
        ).count()
        
        return jsonify({
            'pending_orders': pending_count,
            'orders_needing_approval': approval_count,
            'shipped_orders': shipped_count,
            'overdue_orders': overdue_count,
            'total_pending_value': float(total_pending_value)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/generate-recommendations', methods=['POST'])
@manager_or_admin_required
def generate_order_recommendations():
    """Generate purchase order recommendations"""
    try:
        # Import reorder service
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from services.reorder_service import ReorderService
        
        reorder_service = ReorderService()
        report = reorder_service.generate_reorder_report()
        
        return jsonify({
            'success': True,
            'recommendations': report['items'],
            'generated_at': report['generated_at'],
            'total_items': len(report['items'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500