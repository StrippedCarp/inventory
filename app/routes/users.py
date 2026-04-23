from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.user import User
from app.utils.auth_decorators import admin_required
from app.utils.organization_context import get_organization_id, get_user_id

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Get all users in current organization"""
    try:
        org_id = get_organization_id()
        users = User.query.filter_by(organization_id=org_id).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get a specific user in current organization"""
    try:
        org_id = get_organization_id()
        user = User.query.filter_by(id=user_id, organization_id=org_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """Create a new user in current organization"""
    try:
        org_id = get_organization_id()
        data = request.get_json()
        
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        # Check if username exists in this organization
        if User.query.filter_by(username=data['username'], organization_id=org_id).first():
            return jsonify({'message': 'Username already exists'}), 409
        
        # Check if email exists in this organization
        if User.query.filter_by(email=data['email'], organization_id=org_id).first():
            return jsonify({'message': 'Email already exists'}), 409
        
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'viewer'),
            organization_id=org_id
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update a user in current organization"""
    try:
        org_id = get_organization_id()
        user = User.query.filter_by(id=user_id, organization_id=org_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if data.get('username') and data['username'] != user.username:
            if User.query.filter_by(username=data['username'], organization_id=org_id).first():
                return jsonify({'message': 'Username already exists'}), 409
            user.username = data['username']
        
        if data.get('email') and data['email'] != user.email:
            if User.query.filter_by(email=data['email'], organization_id=org_id).first():
                return jsonify({'message': 'Email already exists'}), 409
            user.email = data['email']
        
        if data.get('password'):
            user.set_password(data['password'])
        
        if data.get('role'):
            user.role = data['role']
        
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete a user from current organization"""
    try:
        org_id = get_organization_id()
        current_user_id = get_user_id()
        
        user = User.query.filter_by(id=user_id, organization_id=org_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prevent deleting yourself
        if user_id == current_user_id:
            return jsonify({'error': 'Validation error', 'message': 'Cannot delete yourself'}), 400
        
        # Set user_id to NULL in activity_logs instead of deleting
        # This preserves the activity history with username
        from app.models.activity_log import ActivityLog
        ActivityLog.query.filter_by(user_id=user_id).update({'user_id': None})
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
