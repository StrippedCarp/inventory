from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.utils.organization_context import get_organization_id
from app.models.batch import Batch, BatchTransaction
from app.models.product import Product
from datetime import datetime, date

batches_bp = Blueprint('batches', __name__)

@batches_bp.route('', methods=['GET'])
@jwt_required()
def get_batches():
    """Get all batches with optional filters"""
    try:
        org_id = get_organization_id()
        product_id = request.args.get('product_id', type=int)
        status = request.args.get('status')
        
        query = db.session.query(Batch).join(Product).filter(Product.organization_id == org_id)
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        if status:
            query = query.filter_by(status=status)
        
        batches = query.order_by(Batch.expiry_date.asc()).all()
        return jsonify([batch.to_dict() for batch in batches]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/<int:batch_id>', methods=['GET'])
@jwt_required()
def get_batch(batch_id):
    """Get batch details"""
    try:
        org_id = get_organization_id()
        batch = db.session.query(Batch).join(Product).filter(
            Batch.id == batch_id,
            Product.organization_id == org_id
        ).first()
        if not batch:
            return jsonify({'message': 'Batch not found'}), 404
        
        batch_dict = batch.to_dict()
        batch_dict['transactions'] = [t.to_dict() for t in batch.transactions]
        return jsonify(batch_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('', methods=['POST'])
@jwt_required()
def create_batch():
    """Create new batch"""
    try:
        org_id = get_organization_id()
        data = request.get_json()
        
        # Validate product exists and belongs to user
        product = Product.query.filter_by(id=data['product_id'], user_id=user_id).first()
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        # Parse dates
        manufacture_date = datetime.strptime(data['manufacture_date'], '%Y-%m-%d').date() if data.get('manufacture_date') else None
        expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None
        
        batch = Batch(
            product_id=data['product_id'],
            batch_number=data['batch_number'],
            quantity=data['quantity'],
            cost_per_unit=data['cost_per_unit'],
            manufacture_date=manufacture_date,
            expiry_date=expiry_date,
            supplier_id=data.get('supplier_id')
        )
        
        db.session.add(batch)
        db.session.commit()
        
        return jsonify(batch.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/<int:batch_id>', methods=['PUT'])
@jwt_required()
def update_batch(batch_id):
    """Update batch"""
    try:
        org_id = get_organization_id()
        batch = db.session.query(Batch).join(Product).filter(
            Batch.id == batch_id,
            Product.organization_id == org_id
        ).first()
        if not batch:
            return jsonify({'message': 'Batch not found'}), 404
        
        data = request.get_json()
        
        if 'quantity' in data:
            batch.quantity = data['quantity']
        if 'cost_per_unit' in data:
            batch.cost_per_unit = data['cost_per_unit']
        if 'status' in data:
            batch.status = data['status']
        if 'expiry_date' in data:
            batch.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify(batch.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/expiring', methods=['GET'])
@jwt_required()
def get_expiring_batches():
    """Get batches expiring soon"""
    try:
        org_id = get_organization_id()
        days = request.args.get('days', 30, type=int)
        today = date.today()
        
        batches = db.session.query(Batch).join(Product).filter(
            Product.organization_id == org_id,
            Batch.expiry_date.isnot(None),
            Batch.expiry_date <= date.today().replace(day=today.day + days),
            Batch.status == 'active',
            Batch.quantity > 0
        ).order_by(Batch.expiry_date.asc()).all()
        
        return jsonify([batch.to_dict() for batch in batches]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/valuation', methods=['GET'])
@jwt_required()
def get_inventory_valuation():
    """Calculate inventory valuation using FIFO or LIFO"""
    try:
        org_id = get_organization_id()
        method = request.args.get('method', 'fifo').lower()  # fifo or lifo
        product_id = request.args.get('product_id', type=int)
        
        query = db.session.query(Batch).join(Product).filter(
            Product.organization_id == org_id,
            Batch.status == 'active',
            Batch.quantity > 0
        )
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if method == 'fifo':
            batches = query.order_by(Batch.received_date.asc()).all()
        else:  # lifo
            batches = query.order_by(Batch.received_date.desc()).all()
        
        total_value = 0
        total_quantity = 0
        batch_details = []
        
        for batch in batches:
            value = batch.quantity * batch.cost_per_unit
            total_value += value
            total_quantity += batch.quantity
            
            batch_details.append({
                'batch_number': batch.batch_number,
                'product_name': batch.product.name,
                'quantity': batch.quantity,
                'cost_per_unit': batch.cost_per_unit,
                'total_value': value,
                'received_date': batch.received_date.isoformat()
            })
        
        return jsonify({
            'method': method.upper(),
            'total_value': total_value,
            'total_quantity': total_quantity,
            'average_cost': total_value / total_quantity if total_quantity > 0 else 0,
            'batches': batch_details
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@batches_bp.route('/allocate', methods=['POST'])
@jwt_required()
def allocate_batch():
    """Allocate quantity from batch (FIFO by default)"""
    try:
        org_id = get_organization_id()
        data = request.get_json()
        product_id = data['product_id']
        quantity_needed = data['quantity']
        method = data.get('method', 'fifo').lower()
        
        # Get available batches for user's products
        query = db.session.query(Batch).join(Product).filter(
            Product.organization_id == org_id,
            Batch.product_id == product_id,
            Batch.status == 'active',
            Batch.quantity > 0
        )
        
        if method == 'fifo':
            batches = query.order_by(Batch.received_date.asc()).all()
        else:
            batches = query.order_by(Batch.received_date.desc()).all()
        
        allocated = []
        remaining = quantity_needed
        
        for batch in batches:
            if remaining <= 0:
                break
            
            allocated_qty = min(batch.quantity, remaining)
            allocated.append({
                'batch_id': batch.id,
                'batch_number': batch.batch_number,
                'quantity': allocated_qty,
                'cost_per_unit': batch.cost_per_unit
            })
            remaining -= allocated_qty
        
        if remaining > 0:
            return jsonify({
                'message': 'Insufficient stock in batches',
                'available': quantity_needed - remaining,
                'shortage': remaining
            }), 400
        
        return jsonify({
            'allocated': allocated,
            'total_quantity': quantity_needed,
            'total_cost': sum(a['quantity'] * a['cost_per_unit'] for a in allocated)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
