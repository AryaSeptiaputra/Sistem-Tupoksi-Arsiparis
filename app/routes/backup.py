import os
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
# Import service yang sudah diupdate
from app.services.backup import perform_database_backup, perform_database_restore, BACKUP_DIR
from app.models.backup import Backup
from app.services.user import get_users_by_keys 

backup_bp = Blueprint('backup', __name__)

def get_current_user_obj(db_session: Session):
    """Helper untuk mengambil object User berdasarkan JWT Identity (NUPTK)."""
    current_nuptk = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_nuptk})
    return users[0] if users else None

@backup_bp.route('/manual', methods=['POST'])
@jwt_required()
def trigger_manual_backup():
    """Trigger backup manual."""
    db_session: Session = SessionLocal()
    current_user = None
    
    try:
        current_user = get_current_user_obj(db_session)
    except Exception as e:
        print(f"Warning: Could not resolve user ID for backup log. Error: {e}")
    finally:
        db_session.close()

    try:
        result = perform_database_backup(
            user_id=current_user.id if current_user else None
        )
        return jsonify({
            "message": "Backup created successfully",
            "data": result
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@backup_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_backup_logs():
    """Mengambil riwayat backup."""
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

# --- ENDPOINT DOWNLOAD ---
@backup_bp.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_backup_file(filename):
    """Mengunduh file backup."""
    try:
        # Validasi sederhana: pastikan file ada di folder backup
        full_path = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(full_path):
            return jsonify({"error": "File tidak ditemukan"}), 404

        # Menggunakan send_from_directory agar aman dari path traversal
        return send_from_directory(
            directory=BACKUP_DIR, 
            path=filename, 
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": f"Gagal mengunduh file: {str(e)}"}), 500

# --- ENDPOINT RESTORE ---
@backup_bp.route('/restore', methods=['POST'])
@jwt_required()
def restore_database():
    """Merestore database dari file yang dipilih."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Parameter filename wajib ada"}), 400
    
    filename = data['filename']

    try:
        result = perform_database_restore(filename)
        return jsonify(result), 200

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500