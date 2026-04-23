from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.user import User
from app.models.organization import Organization
from app.models.invitation import Invitation
from app.utils.auth_decorators import admin_required, manager_or_admin_required
from app.utils.organization_context import get_organization_id, get_user_id
from app.utils.notification_service import NotificationService
from app.utils.activity_logger import log_activity
from datetime import datetime, timedelta
import os

organizations_bp = Blueprint('organizations', __name__)

@organizations_bp.route('/settings', methods=['GET'])
@jwt_required()
@manager_or_admin_required
def get_settings():
    """Get organization settings (admin and manager only)"""
    try:
        org_id = get_organization_id()
        org = Organization.query.get(org_id)
        
        if not org:
            return jsonify({'error': 'Organization not found'}), 404
        
        member_count = User.query.filter_by(organization_id=org_id).count()
        
        return jsonify({
            'id': org.id,
            'name': org.name,
            'created_at': org.created_at.isoformat(),
            'member_count': member_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/settings', methods=['PUT'])
@jwt_required()
@admin_required
def update_settings():
    """Update organization settings (admin only)"""
    try:
        org_id = get_organization_id()
        org = Organization.query.get(org_id)
        
        if not org:
            return jsonify({'error': 'Organization not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            if not data['name'].strip():
                return jsonify({'error': 'Validation error', 'message': 'Organization name cannot be empty'}), 400
            org.name = data['name'].strip()
        
        db.session.commit()
        
        # Log activity
        user_id = get_user_id()
        user = User.query.get(user_id)
        if user:
            log_activity(org_id, user_id, user.username, 'updated', 'organization settings', org.name)
        
        member_count = User.query.filter_by(organization_id=org_id).count()
        
        return jsonify({
            'id': org.id,
            'name': org.name,
            'created_at': org.created_at.isoformat(),
            'member_count': member_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/members', methods=['GET'])
@jwt_required()
@manager_or_admin_required
def get_members():
    """Get all organization members (admin and manager only)"""
    try:
        org_id = get_organization_id()
        current_user_id = get_user_id()
        
        members = User.query.filter_by(organization_id=org_id).order_by(User.created_at.desc()).all()
        
        return jsonify([{
            'id': member.id,
            'username': member.username,
            'email': member.email,
            'role': member.role,
            'created_at': member.created_at.isoformat(),
            'is_current_user': member.id == current_user_id
        } for member in members]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/members/<int:member_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
def update_member_role(member_id):
    """Update member role (admin only)"""
    try:
        org_id = get_organization_id()
        current_user_id = get_user_id()
        
        # Cannot change your own role
        if member_id == current_user_id:
            return jsonify({'error': 'Validation error', 'message': 'Cannot change your own role'}), 400
        
        member = User.query.filter_by(id=member_id, organization_id=org_id).first()
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Cannot change admin roles
        if member.role == 'admin':
            return jsonify({'error': 'Validation error', 'message': 'Cannot change admin roles'}), 400
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Validation error', 'message': 'Role is required'}), 400
        
        # Can only set to manager or viewer
        if new_role not in ['manager', 'viewer']:
            return jsonify({'error': 'Validation error', 'message': 'Role must be manager or viewer'}), 400
        
        member.role = new_role
        db.session.commit()
        
        # Log activity
        user_id = get_user_id()
        user = User.query.get(user_id)
        if user:
            log_activity(org_id, user_id, user.username, f'changed role to {new_role} for', 'member', member.username)
        
        return jsonify({
            'id': member.id,
            'username': member.username,
            'email': member.email,
            'role': member.role,
            'created_at': member.created_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/members/<int:member_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def remove_member(member_id):
    """Remove member from organization (admin only)"""
    try:
        org_id = get_organization_id()
        current_user_id = get_user_id()
        
        # Cannot remove yourself
        if member_id == current_user_id:
            return jsonify({'error': 'Validation error', 'message': 'Cannot remove yourself'}), 400
        
        member = User.query.filter_by(id=member_id, organization_id=org_id).first()
        
        if not member:
            return jsonify({'error': 'Member not found'}), 404
        
        # Cannot remove other admins
        if member.role == 'admin':
            return jsonify({'error': 'Validation error', 'message': 'Cannot remove admin users'}), 400
        
        # Remove from organization by setting organization_id to null
        member_name = member.username
        member.organization_id = None
        db.session.commit()
        
        # Log activity
        user_id = get_user_id()
        user = User.query.get(user_id)
        if user:
            log_activity(org_id, user_id, user.username, 'removed', 'member', member_name)
        
        return jsonify({'message': 'Member removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/invitations', methods=['GET'])
@jwt_required()
@admin_required
def get_invitations():
    """Get all organization invitations (admin only)"""
    try:
        org_id = get_organization_id()
        
        invitations = Invitation.query.filter_by(organization_id=org_id).order_by(Invitation.created_at.desc()).all()
        
        return jsonify([{
            'id': inv.id,
            'email': inv.email,
            'role': inv.role,
            'created_at': inv.created_at.isoformat(),
            'expires_at': inv.expires_at.isoformat(),
            'accepted_at': inv.accepted_at.isoformat() if inv.accepted_at else None,
            'status': 'accepted' if inv.accepted_at else ('expired' if datetime.utcnow() > inv.expires_at else 'pending')
        } for inv in invitations]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/invitations/<int:invitation_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def revoke_invitation(invitation_id):
    """Revoke pending invitation (admin only)"""
    try:
        org_id = get_organization_id()
        
        invitation = Invitation.query.filter_by(id=invitation_id, organization_id=org_id).first()
        
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404
        
        # Can only revoke if not yet accepted
        if invitation.accepted_at:
            return jsonify({'error': 'Validation error', 'message': 'Cannot revoke accepted invitation'}), 400
        
        db.session.delete(invitation)
        db.session.commit()
        
        return jsonify({'message': 'Invitation revoked successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@organizations_bp.route('/invitations/<int:invitation_id>/resend', methods=['POST'])
@jwt_required()
@admin_required
def resend_invitation(invitation_id):
    """Resend invitation with new token (admin only)"""
    try:
        org_id = get_organization_id()
        
        invitation = Invitation.query.filter_by(id=invitation_id, organization_id=org_id).first()
        
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404
        
        # Can only resend if not yet accepted
        if invitation.accepted_at:
            return jsonify({'error': 'Validation error', 'message': 'Cannot resend accepted invitation'}), 400
        
        # Generate new token and reset expiry
        invitation.token = Invitation.generate_token()
        invitation.expires_at = datetime.utcnow() + timedelta(hours=48)
        db.session.commit()
        
        # Send invitation email
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        invite_link = f"{frontend_url}/invite?token={invitation.token}"
        
        subject = "You're invited to join our team (Resent)"
        message = f"""
Hello,

You've been invited to join our inventory management system as a {invitation.role}.

Click the link below to accept the invitation and create your account:
{invite_link}

This invitation expires in 48 hours.

If you didn't expect this invitation, you can safely ignore this email.
        """.strip()
        
        NotificationService.send_email(invitation.email, subject, message)
        
        return jsonify({
            'message': 'Invitation resent successfully',
            'invitation': {
                'id': invitation.id,
                'email': invitation.email,
                'role': invitation.role,
                'expires_at': invitation.expires_at.isoformat(),
                'status': 'pending'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
