from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.supplier import Supplier
from app.models.supplier_contact import SupplierContact
from app.models.user import User
from app.utils.auth_decorators import admin_required, manager_or_admin_required
from app.utils.notification_service import NotificationService

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('', methods=['GET'])
def get_suppliers():
    """Get all suppliers"""
    try:
        suppliers = Supplier.query.all()
        return jsonify([supplier.to_dict() for supplier in suppliers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get single supplier"""
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'message': 'Supplier not found'}), 404
        return jsonify(supplier.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('', methods=['POST'])
def create_supplier():
    """Create new supplier"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        supplier = Supplier(
            name=data['name'],
            contact_person=data.get('contact_person'),
            email=data['email'],
            phone=data.get('phone'),
            lead_time_days=data.get('lead_time_days', 7),
            rating=data.get('rating', 5.0)
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify(supplier.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """Update supplier"""
    try:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return jsonify({'message': 'Supplier not found'}), 404
        
        data = request.get_json()
        updatable_fields = ['name', 'contact_person', 'email', 'phone', 'lead_time_days', 'rating']
        
        for field in updatable_fields:
            if field in data:
                setattr(supplier, field, data[field])
        
        db.session.commit()
        return jsonify(supplier.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/<int:supplier_id>/contact', methods=['POST'])
@jwt_required(optional=True)
def contact_supplier(supplier_id):
    """Contact supplier via email or SMS"""
    try:
        user_id = get_jwt_identity() or 1  # Default to user 1 if no JWT
        user = User.query.get(user_id)
        supplier = Supplier.query.get(supplier_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if not supplier:
            return jsonify({'message': 'Supplier not found'}), 404
        
        data = request.get_json()
        message = data.get('message', '')
        contact_method = data.get('contact_method', 'email')
        
        if not message:
            return jsonify({'message': 'Message is required'}), 400
        
        contact = SupplierContact(
            user_id=user_id,
            supplier_id=supplier_id,
            message=message,
            contact_method=contact_method
        )
        
        success = False
        if contact_method == 'email' and supplier.email:
            subject = f"Contact Request from {user.username}"
            full_message = f"From: {user.username} ({user.email})\n\n{message}"
            success = NotificationService.send_email(supplier.email, subject, full_message)
        elif contact_method == 'sms' and supplier.phone:
            sms_message = f"{user.username}: {message}"
            success = NotificationService.send_sms(supplier.phone, sms_message)
        
        contact.status = 'sent' if success else 'failed'
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'message': 'Contact request sent successfully' if success else 'Failed to send contact request',
            'contact': contact.to_dict()
        }), 200
    except Exception as e:
        print(f"Supplier contact error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/contacts', methods=['GET'])
@jwt_required()
def get_my_contacts():
    """Get user's supplier contact history"""
    try:
        user_id = get_jwt_identity()
        contacts = SupplierContact.query.filter_by(user_id=user_id).order_by(SupplierContact.created_at.desc()).all()
        return jsonify([contact.to_dict() for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
