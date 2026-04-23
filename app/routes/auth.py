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
    """Register a new user with their own organization"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['username', 'email', 'password', 'organization_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': 'Validation error', 'message': f'{field} is required'}), 400
        
        # Validate password length
        if len(data['password']) < 6:
            return jsonify({'error': 'Validation error', 'message': 'Password must be at least 6 characters'}), 400
        
        # Validate organization name
        if not data['organization_name'].strip():
            return jsonify({'error': 'Validation error', 'message': 'Organization name cannot be empty'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Validation error', 'message': 'Username already exists'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Validation error', 'message': 'Email already exists'}), 409
        
        # Create new organization
        from app.models.organization import Organization
        org = Organization(
            name=data['organization_name'],
            email=data['email']
        )
        db.session.add(org)
        db.session.flush()  # Get org.id without committing
        
        # Create new user as admin of their organization
        user = User(
            username=data['username'],
            email=data['email'],
            role='admin',  # Founder is always admin
            organization_id=org.id
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        from app.utils.notification_service import NotificationService
        welcome_subject = "Welcome to Inventory Management System"
        welcome_message = f"""
Hello {user.username},

Welcome to the Inventory Management System!

Your organization "{org.name}" has been successfully created, and you are the administrator.

Account Details:
- Username: {user.username}
- Email: {user.email}
- Role: Admin
- Organization: {org.name}

As an admin, you can:
- Manage all products and inventory
- Invite team members (managers and viewers)
- Access all system features
- View analytics and reports

Key Features:
- Product Management
- Inventory Tracking
- Customer Management
- Supplier Management
- ML-based Demand Forecasting
- Low Stock Alerts
- Team Collaboration

You can invite team members from the User Management page.

If you have any questions, please don't hesitate to reach out.

Best regards,
Inventory Management Team
        """.strip()
        
        NotificationService.send_email(user.email, welcome_subject, welcome_message)
        
        return jsonify({
            'message': 'Organization and account created successfully. Welcome email sent!',
            'user': user.to_dict(),
            'organization_name': org.name
        }), 201
        
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Validate required fields
        if not username:
            return jsonify({'error': 'Validation error', 'message': 'Username is required'}), 400
        
        if not password:
            return jsonify({'error': 'Validation error', 'message': 'Password is required'}), 400
        
        # Find user in database
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Get organization name
        from app.models.organization import Organization
        org = Organization.query.get(user.organization_id)
        org_name = org.name if org else 'Unknown Organization'
        
        # Create tokens with organization_id and name
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'username': user.username,
                'organization_id': user.organization_id,
                'organization_name': org_name
            }
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims={
                'organization_id': user.organization_id,
                'organization_name': org_name
            }
        )
        
        # Add organization name to user dict
        user_dict = user.to_dict()
        user_dict['organization_name'] = org_name
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_dict
        })
        
    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        print("Refresh endpoint called")
        current_user_id = get_jwt_identity()
        print(f"User ID from token: {current_user_id}")
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get organization name
        from app.models.organization import Organization
        org = Organization.query.get(user.organization_id)
        org_name = org.name if org else 'Unknown Organization'
        
        new_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'username': user.username,
                'organization_id': user.organization_id,
                'organization_name': org_name
            }
        )
        
        return jsonify({'access_token': new_token})
        
    except Exception as e:
        import traceback
        print(f"Refresh error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get organization name
        from app.models.organization import Organization
        org = Organization.query.get(user.organization_id)
        
        user_dict = user.to_dict()
        if org:
            user_dict['organization_name'] = org.name
        
        return jsonify(user_dict)
        
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
        user = User.query.get(int(current_user_id))
        
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