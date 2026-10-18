import os
from flask import Blueprint, jsonify, request, send_from_directory
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.errors import BackupError, RestoreError
from app.services.backup import perform_database_backup, perform_database_restore, get_all_logs, BACKUP_DIR
from app.services.user import get_user
from app.utils.current_user import get_current_user_id
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/manual', methods=['POST'])
@jwt_required()
def trigger_manual_backup() -> ResponseReturnValue:
    """Membuat backup database atas nama akun yang login.

    Returns:
        201 dengan nama dan path file backup, atau 500 bila backup gagal.
    """
    db_session: Session = SessionLocal()
    triggered_by = "SYSTEM"

    try:
        user = get_user(db_session, get_current_user_id())
        if user:
            triggered_by = user.display_name
    except SQLAlchemyError as e:
        logger.warning(f"Nama akun untuk log backup tidak terbaca: {e}", exc_info=True)
    finally:
        db_session.close()

    try:
        result = perform_database_backup(triggered_by=triggered_by)

        return jsonify({
            "message": "Backup created successfully",
            "data": result
        }), 201

    except BackupError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Backup manual gagal: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@backup_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_backup_logs() -> ResponseReturnValue:
    """Mengambil riwayat backup dari file log JSON.

    Returns:
        200 dengan daftar riwayat, atau 500 bila terjadi error.
    """
    try:
        logs = get_all_logs()
        return jsonify(logs), 200
    except Exception as e:
        logger.error(f"Gagal membaca riwayat backup: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@backup_bp.route('/download/<path:filename>', methods=['GET'])
@jwt_required()
def download_backup_file(filename: str) -> ResponseReturnValue:
    """Mengunduh file backup.

    Args:
        filename: Nama file di folder backup.

    Returns:
        File backup, 404 bila tidak ada, atau 500 bila gagal dikirim.
    """
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
        logger.error(f"Gagal mengunduh file backup {filename}: {e}", exc_info=True)
        return jsonify({"error": f"Gagal mengunduh file: {str(e)}"}), 500

@backup_bp.route('/restore', methods=['POST'])
@jwt_required()
def restore_database() -> ResponseReturnValue:
    """Memulihkan database dari file backup pilihan.

    Body JSON: `filename`.

    Returns:
        200 bila berhasil, 400 bila `filename` kosong, 404 bila file tidak
        ada, atau 500 bila pemulihan gagal.
    """
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Parameter filename wajib ada"}), 400

    filename = data['filename']

    try:
        result = perform_database_restore(filename)
        return jsonify(result), 200

    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except RestoreError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Restore gagal: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
