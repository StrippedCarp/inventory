from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Alert
from app.models.product import Product
from app.models.inventory import Inventory
from app.utils.auth_decorators import manager_or_admin_required
from datetime import datetime

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('', methods=['GET'])
def get_alerts():
    """Get all alerts with filtering"""
    try:
        status = request.args.get('status', 'active')
        severity = request.args.get('severity')
        alert_type = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Simple query without join to avoid issues
        query = Alert.query
        
        # Apply filters
        if status:
            query = query.filter(Alert.status == status)
        
        if severity:
            query = query.filter(Alert.severity == severity)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        # Get alerts
        alerts = query.order_by(Alert.created_at.desc()).limit(per_page).all()
        
        result = {
            'alerts': [alert.to_dict() for alert in alerts],
            'total': len(alerts),
            'pages': 1,
            'current_page': page
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/<int:alert_id>/resolve', methods=['PUT'])
@manager_or_admin_required
def resolve_alert(alert_id):
    """Resolve an alert"""
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'message': 'Alert not found'}), 404
        
        alert.status = 'resolved'
        db.session.commit()
        
        return jsonify({
            'message': 'Alert resolved successfully',
            'alert': alert.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/check-stock-levels', methods=['POST'])
def check_stock_levels():
    """Check all products for low stock and create/update alerts"""
    try:
        # First, resolve all existing low_stock alerts
        Alert.query.filter_by(
            alert_type='low_stock',
            status='active'
        ).update({'status': 'resolved'})
        
        # Get all products with low stock
        low_stock_items = db.session.query(Inventory, Product).join(Product).filter(
            Inventory.quantity_on_hand <= Product.reorder_point
        ).all()
        
        alerts_created = 0
        
        for inventory, product in low_stock_items:
            if inventory.quantity_on_hand == 0:
                severity = 'critical'
                message = f'{product.name} is out of stock'
            else:
                severity = 'warning'
                message = f'{product.name} stock is low ({inventory.quantity_on_hand} units, reorder at {product.reorder_point})'
            
            alert = Alert(
                product_id=product.id,
                alert_type='low_stock',
                severity=severity,
                message=message,
                status='active'
            )
            
            db.session.add(alert)
            alerts_created += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Stock level check completed. {alerts_created} alerts active.',
            'alerts_created': alerts_created
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_alerts_summary():
    """Get alerts summary statistics"""
    try:
        total_active = Alert.query.filter_by(status='active').count()
        
        critical_count = Alert.query.filter_by(
            status='active', 
            severity='critical'
        ).count()
        
        warning_count = Alert.query.filter_by(
            status='active', 
            severity='warning'
        ).count()
        
        low_stock_count = Alert.query.filter_by(
            status='active',
            alert_type='low_stock'
        ).count()
        
        return jsonify({
            'total_active_alerts': total_active,
            'critical_alerts': critical_count,
            'warning_alerts': warning_count,
            'low_stock_alerts': low_stock_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@alerts_bp.route('', methods=['POST'])
@manager_or_admin_required
def create_alert():
    """Create a custom alert"""
    try:
        data = request.get_json()
        
        required_fields = ['product_id', 'alert_type', 'severity', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Verify product exists
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        alert = Alert(
            product_id=data['product_id'],
            alert_type=data['alert_type'],
            severity=data['severity'],
            message=data['message'],
            status='active'
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify(alert.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500