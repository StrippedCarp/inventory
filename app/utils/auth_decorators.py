from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

def require_role(*allowed_roles):
    """Decorator to require specific roles for access"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'message': f'Access denied. Required roles: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return require_role('admin')(f)

def manager_or_admin_required(f):
    """Decorator to require manager or admin role"""
    return require_role('admin', 'manager')(f)