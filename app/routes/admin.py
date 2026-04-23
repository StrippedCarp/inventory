from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.supplier_contact import SupplierContact
from app.models.customer_contact import CustomerContact
from app.utils.auth_decorators import manager_or_admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/supplier-contacts', methods=['GET'])
@manager_or_admin_required
def get_all_supplier_contacts():
    """Get all supplier contact communications (Admin/Manager only)"""
    try:
        contacts = SupplierContact.query.order_by(SupplierContact.created_at.desc()).all()
        return jsonify([contact.to_dict() for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/customer-contacts', methods=['GET'])
@manager_or_admin_required
def get_all_customer_contacts():
    """Get all customer contact communications (Admin/Manager only)"""
    try:
        contacts = CustomerContact.query.order_by(CustomerContact.created_at.desc()).all()
        return jsonify([contact.to_dict() for contact in contacts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
