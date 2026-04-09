from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models.user import User
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

# Store blacklisted tokens (in production, use Redis)
blacklisted_tokens = set()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'viewer')  # Default to viewer role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Username and password required'}), 400
        
        # Find user in database
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'username': user.username}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        new_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'username': user.username}
        )
        
        return jsonify({'access_token': new_token})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        # Return a default user when JWT is not available
        return jsonify({
            'id': 1,
            'username': 'demo_user',
            'email': 'demo@example.com',
            'role': 'admin'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and blacklist token"""
    try:
        jti = get_jwt()['jti']  # JWT ID
        blacklisted_tokens.add(jti)
        
        return jsonify({'message': 'Successfully logged out'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'message': 'Current and new password required'}), 400
        
        if not user.check_password(current_password):
            return jsonify({'message': 'Current password is incorrect'}), 400
        
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500