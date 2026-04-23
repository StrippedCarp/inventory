from flask_jwt_extended import get_jwt

def get_organization_id():
    """Get organization_id from JWT claims"""
    claims = get_jwt()
    return claims.get('organization_id')

def get_user_id():
    """Get user_id from JWT identity"""
    from flask_jwt_extended import get_jwt_identity
    return int(get_jwt_identity())
