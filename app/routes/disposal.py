from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from app import db
from app.services.disposal import get_expired_archives, execute_disposal
from app.services.log import create_log
from app.utils.current_user import get_current_user_id
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

disposal_bp = Blueprint('disposal', __name__)

@disposal_bp.route('/check', methods=['GET'])
@jwt_required()
def check_expiry_route() -> ResponseReturnValue:
    """Mengambil daftar arsip yang sudah boleh dimusnahkan.

    Returns:
        200 dengan daftar arsip kedaluwarsa, atau 500 bila terjadi error.
    """
    db_session: Session = db.SessionLocal()
    try:
        results = get_expired_archives(db_session)
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Gagal mengecek arsip kedaluwarsa: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@disposal_bp.route('/execute', methods=['POST'])
@jwt_required()
def execute_route() -> ResponseReturnValue:
    """Memusnahkan arsip pilihan.

    Body JSON: array arsip, atau object dengan kunci `items`; tiap arsip
    berisi `table_source` dan `id`.

    Returns:
        200 dengan jumlah arsip yang dimusnahkan, 400 bila tidak ada pilihan,
        atau 500 bila terjadi error.
    """
    db_session: Session = db.SessionLocal()
    try:
        data = request.json
        
        items = []
        if isinstance(data, list):
            # Front-end bisa mengirim array langsung: [...]
            items = data
        elif isinstance(data, dict):
            # atau object: { "items": [...] }
            items = data.get('items', [])
        
        if not items:
            return jsonify({"error": "No items selected"}), 400

        user_id = get_current_user_id()

        count = execute_disposal(db_session, items, user_id)

        create_log(db_session, user_id, f"Melakukan Pemusnahan Arsip: {count} dokumen.")
        
        db_session.commit() # Pastikan commit jika belum dilakukan di service
        return jsonify({"message": f"Berhasil memusnahkan {count} arsip.", "count": count}), 200
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"Gagal memusnahkan arsip: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()