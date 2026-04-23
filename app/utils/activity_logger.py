from app import db
from app.models.activity_log import ActivityLog

def log_activity(org_id, user_id, username, action, resource_type, resource_name):
    """
    Log user activity to the database.
    Silently fails to prevent breaking main operations.
    """
    try:
        description = f"{username} {action} {resource_type} {resource_name}"
        
        activity = ActivityLog(
            organization_id=org_id,
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_name=resource_name,
            description=description
        )
        
        db.session.add(activity)
        db.session.commit()
    except Exception:
        # Silently fail - don't break main operations
        db.session.rollback()
