from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.backup import perform_database_backup
from app.models.backup import Backup

from app.services.user import get_users_by_keys 

backup_bp = Blueprint('backup', __name__)

def get_current_user_obj(db_session: Session):
    """Helper function to retrieve the currently logged-in user object.

    Uses the JWT identity (NUPTK) from the request context to fetch
    the full User object from the database using the plural service with a filter.

    Args:
        db_session (Session): The active database session.

    Returns:
        User | None: The User object if found, otherwise None.
    """
    current_nuptk = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_nuptk})
    return users[0] if users else None

@backup_bp.route('/manual', methods=['POST'])
@jwt_required()
def trigger_manual_backup():
    """Triggers a manual database backup immediately.

    Requires a valid JWT access token. The ID of the user requesting the
    backup will be recorded in the backup logs.

    Args:
        None.

    Returns:
        tuple[Response, int]:
            * 201: JSON dictionary containing the backup filename and path.
            * 500: Error message if the backup process fails.
    """
    db_session: Session = SessionLocal()
    user_id = None
    
    try:
        user_id = get_current_user_obj(db_session)
    except Exception as e:
        print(f"Warning: Could not resolve user ID for backup log. Error: {e}")
    finally:
        db_session.close()

    try:
        result = perform_database_backup(user_id=user_id)
        return jsonify({
            "message": "Backup created successfully",
            "data": result
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@backup_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_backup_logs():
    """Retrieves the history of database backups.

    Returns a list of backup logs, sorted by creation time (newest first).

    Returns:
        tuple[Response, int]:
            * 200: JSON list of backup log objects.
    """
    db_session: Session = SessionLocal()
    try:
        logs = db_session.query(Backup).order_by(Backup.created_at.desc()).limit(50).all()
        
        results = []
        for log in logs:
            results.append({
                "id": log.id,
                "filename": log.filename,
                "status": log.status,
                "message": log.message,
                "user_id": log.user_id,
                "created_at": log.created_at.isoformat() if log.created_at else None
            })
            
        return jsonify(results), 200
    finally:
        db_session.close()