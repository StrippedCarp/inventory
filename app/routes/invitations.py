from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.invitation import Invitation
from app.models.user import User
from app.utils.notification_service import NotificationService
from app.utils.organization_context import get_organization_id, get_user_id
from app.utils.auth_decorators import admin_required
from app.utils.activity_logger import log_activity
import os

invitations_bp = Blueprint('invitations', __name__)

@invitations_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_invitation():
    """Admin creates invitation and sends email"""
    data = request.get_json()
    email = data.get('email')
    role = data.get('role')
    
    # Validate required fields
    if not email:
        return jsonify({'error': 'Validation error', 'message': 'Email is required'}), 400
    
    if not role:
        return jsonify({'error': 'Validation error', 'message': 'Role is required'}), 400
    
    # Validate role value
    if role not in ['manager', 'viewer']:
        return jsonify({'error': 'Validation error', 'message': 'Role must be manager or viewer'}), 400
    
    organization_id = get_organization_id()
    user_id = get_user_id()
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400
    
    # Check for pending invitation
    pending = Invitation.query.filter_by(
        email=email,
        organization_id=organization_id,
        accepted_at=None
    ).first()
    
    if pending and pending.is_valid():
        return jsonify({'error': 'Invitation already sent to this email'}), 400
    
    # Create invitation
    invitation = Invitation.create_invitation(email, role, organization_id, user_id)
    db.session.add(invitation)
    db.session.commit()
    
    # Send invitation email
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    invite_link = f"{frontend_url}/invite?token={invitation.token}"
    
    subject = "You're invited to join our team"
    message = f"""
Hello,

You've been invited to join our inventory management system as a {role}.

Click the link below to accept the invitation and create your account:
{invite_link}

This invitation expires in 48 hours.

If you didn't expect this invitation, you can safely ignore this email.
    """.strip()
    
    NotificationService.send_email(email, subject, message)
    
    # Log activity
    user = User.query.get(user_id)
    if user:
        log_activity(organization_id, user_id, user.username, 'sent invitation to', 'user', email)
    
    return jsonify({
        'message': 'Invitation sent successfully',
        'invitation': invitation.to_dict()
    }), 201

@invitations_bp.route('/validate', methods=['GET'])
def validate_invitation():
    """Validate invitation token (public endpoint)"""
    token = request.args.get('token')
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    invitation = Invitation.query.filter_by(token=token).first()
    
    if not invitation:
        return jsonify({'error': 'Invalid invitation token'}), 404
    
    if not invitation.is_valid():
        if invitation.accepted_at:
            return jsonify({'error': 'Invitation already accepted'}), 400
        else:
            return jsonify({'error': 'Invitation expired'}), 400
    
    return jsonify({
        'valid': True,
        'email': invitation.email,
        'role': invitation.role,
        'organization_id': invitation.organization_id
    }), 200

@invitations_bp.route('/accept', methods=['POST'])
def accept_invitation():
    """Accept invitation and create user account (public endpoint)"""
    data = request.get_json()
    token = data.get('token')
    username = data.get('username')
    password = data.get('password')
    
    if not token or not username or not password:
        return jsonify({'error': 'Token, username, and password required'}), 400
    
    invitation = Invitation.query.filter_by(token=token).first()
    
    if not invitation:
        return jsonify({'error': 'Invalid invitation token'}), 404
    
    if not invitation.is_valid():
        if invitation.accepted_at:
            return jsonify({'error': 'Invitation already accepted'}), 400
        else:
            return jsonify({'error': 'Invitation expired'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Create user
    user = User(
        username=username,
        email=invitation.email,
        role=invitation.role,
        organization_id=invitation.organization_id
    )
    user.set_password(password)
    
    # Mark invitation as accepted
    invitation.mark_accepted()
    
    db.session.add(user)
    db.session.commit()
    
    # Log activity
    log_activity(invitation.organization_id, user.id, user.username, 'accepted invitation and joined', 'organization', 'team')
    
    return jsonify({
        'message': 'Account created successfully',
        'user': user.to_dict()
    }), 201

@invitations_bp.route('', methods=['GET'])
@jwt_required()
@admin_required
def list_invitations():
    """List all invitations for organization (admin only)"""
    organization_id = get_organization_id()
    
    invitations = Invitation.query.filter_by(
        organization_id=organization_id
    ).order_by(Invitation.created_at.desc()).all()
    
    return jsonify({
        'invitations': [inv.to_dict() for inv in invitations]
    }), 200
