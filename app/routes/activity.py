from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.activity_log import ActivityLog

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('', methods=['GET'])
@jwt_required()
def get_activities():
    """Get activity logs for the organization"""
    claims = get_jwt()
    org_id = claims.get('organization_id')
    
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 100)  # Cap at 100
    
    activities = ActivityLog.query.filter_by(organization_id=org_id)\
        .order_by(ActivityLog.created_at.desc())\
        .limit(limit)\
        .all()
    
    return jsonify([activity.to_dict() for activity in activities]), 200
