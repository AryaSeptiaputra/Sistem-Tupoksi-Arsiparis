from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from app import db
from app.services.disposal import get_expired_archives, execute_disposal
from app.services.log import create_log
from app.services.user import get_users_by_keys

disposal_bp = Blueprint('disposal', __name__)

def get_current_user_obj(db_session):
    current = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current})
    return users[0] if users else None

@disposal_bp.route('/check', methods=['GET'])
@jwt_required()
def check_expiry_route():
    """API untuk mengecek daftar arsip yang sudah kadaluwarsa hari ini."""
    db_session: Session = db.SessionLocal()
    try:
        results = get_expired_archives(db_session)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@disposal_bp.route('/execute', methods=['POST'])
@jwt_required()
def execute_route():
    """API untuk mengeksekusi pemusnahan berdasarkan ID yang dikirim."""
    data = request.json
    items = data.get('items', []) # List of {id, table_source}
    
    if not items:
        return jsonify({"error": "No items selected"}), 400

    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user: return jsonify({"error": "Auth failed"}), 401

        # Eksekusi Logic
        count = execute_disposal(db_session, items, current_user.id)
        
        # Catat Log Admin
        create_log(db_session, current_user.id, f"Melakukan Pemusnahan Arsip: {count} dokumen.")
        
        return jsonify({"message": f"Berhasil memusnahkan {count} arsip.", "count": count}), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()