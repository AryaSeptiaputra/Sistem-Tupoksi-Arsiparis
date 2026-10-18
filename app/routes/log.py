from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from app.services.log import get_all_logs, get_logs_by_keys
from app import db
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

log_bp = Blueprint('log', __name__)

@log_bp.route('/get_all', methods=['GET'])
@jwt_required()
def get_all_logs_route() -> ResponseReturnValue:
    """Mengambil log aktivitas per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session: Session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_logs(db_session, pagination)
        result.items = [l.to_dict() for l in result.items]
        return success_response(result, "Logs retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil log aktivitas: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally:
        db_session.close()

@log_bp.route('/get_by_keys', methods=['POST'])
@jwt_required()
def get_logs_by_keys_route() -> ResponseReturnValue:
    """Mencari log aktivitas.

    Body JSON: `filters`, misalnya `{"action": "login"}`.

    Returns:
        200 dengan log yang cocok, atau 400 bila `filters` kosong atau
        berisi kolom yang tidak ada.
    """
    data = request.json
    filters = data.get('filters')

    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        logs = get_logs_by_keys(db_session, filters)
        return jsonify([l.to_dict() for l in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()