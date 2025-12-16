import os
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
# Import service dan fungsi baru
from app.services.backup import perform_database_backup, perform_database_restore, get_all_logs, BACKUP_DIR
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
    triggered_by = "SYSTEM"
    
    try:
        user = get_current_user_obj(db_session)
        if user:
            triggered_by = user.username # [UBAH] Ambil nama username langsung
    except Exception as e:
        print(f"Warning: Could not resolve user for backup log. Error: {e}")
    finally:
        db_session.close()

    try:
        # [UBAH] Kirim string nama user, bukan ID integer
        result = perform_database_backup(triggered_by=triggered_by)
        
        return jsonify({
            "message": "Backup created successfully",
            "data": result
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@backup_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_backup_logs():
    """Mengambil riwayat backup dari file JSON."""
    try:
        # [UBAH] Panggil fungsi service yang membaca JSON
        logs = get_all_logs()
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT DOWNLOAD ---
@backup_bp.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_backup_file(filename):
    """Mengunduh file backup."""
    try:
        full_path = os.path.join(BACKUP_DIR, filename)
        if not os.path.exists(full_path):
            return jsonify({"error": "File tidak ditemukan"}), 404

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