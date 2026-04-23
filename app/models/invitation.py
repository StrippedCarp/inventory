from app import db
from datetime import datetime, timedelta
import secrets

class Invitation(db.Model):
    __tablename__ = 'invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    accepted_at = db.Column(db.DateTime, nullable=True)
    invited_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    organization = db.relationship('Organization', backref='invitations')
    inviter = db.relationship('User', backref='sent_invitations')
    
    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(48)
    
    @staticmethod
    def create_invitation(email, role, organization_id, invited_by, hours=48):
        token = Invitation.generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=hours)
        
        invitation = Invitation(
            email=email,
            role=role,
            organization_id=organization_id,
            token=token,
            expires_at=expires_at,
            invited_by=invited_by
        )
        return invitation
    
    def is_valid(self):
        return self.accepted_at is None and datetime.utcnow() < self.expires_at
    
    def mark_accepted(self):
        self.accepted_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'organization_id': self.organization_id,
            'expires_at': self.expires_at.isoformat(),
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'invited_by': self.invited_by,
            'created_at': self.created_at.isoformat()
        }
