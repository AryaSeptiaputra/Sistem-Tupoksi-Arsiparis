from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.classification import (
    create_classification, update_classification, delete_classification, 
    get_all_classifications, get_classifications_by_keys
)
from app.services.log import create_log
from app.utils.current_user import get_current_user_id
from app import db
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

classification_bp = Blueprint('classification', __name__)

@classification_bp.route('/create', methods=['POST'])
@jwt_required()
def create_classification_route() -> ResponseReturnValue:
    """Menambah klasifikasi.

    Body JSON: `name`, `code`, dan kolom retensi opsional.

    Returns:
        201 dengan data klasifikasi, 400 bila isian kurang, 409 bila kode
        atau nama sudah ada, atau 500 bila terjadi error.
    """
    data = request.json
    if not data.get('name') or not data.get('code'):
        return jsonify({"error": "Name and Code are required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        new_cls = create_classification(db_session, data)
        
        try:
            create_log(db_session, get_current_user_id(), f"Menambah Klasifikasi: {new_cls.code} - {new_cls.name}")
        except SQLAlchemyError as e:
            logger.warning(f"Gagal mencatat log tambah klasifikasi: {e}", exc_info=True)

        return jsonify(new_cls.to_dict()), 201

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Kode atau Nama Klasifikasi sudah ada."}), 409
    except Exception as e:
        db_session.rollback()
        logger.error(f"Gagal menambah klasifikasi: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@classification_bp.route('/update', methods=['POST'])
@jwt_required()
def update_classification_route() -> ResponseReturnValue:
    """Mengubah klasifikasi.

    Body JSON: `id` dan kolom yang diubah.

    Returns:
        200 dengan data klasifikasi, 400 bila `id` kosong, 404 bila tidak
        ditemukan, atau 409 bila kode atau nama bentrok.
    """
    data = request.json
    if not data.get('id'):
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated = update_classification(db_session, data['id'], data)
        if not updated:
            return jsonify({"error": "Not found"}), 404
            
        return jsonify(updated.to_dict()), 200

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Duplicate Name/Code"}), 409
    finally:
        db_session.close()

@classification_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_classification_route() -> ResponseReturnValue:
    """Menghapus klasifikasi.

    Body JSON: `id`.

    Returns:
        200 bila terhapus, 404 bila tidak ditemukan, atau 400 bila masih
        dipakai arsip.
    """
    data = request.json
    if not data.get('id'):
        return jsonify({"error": "ID required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_classification(db_session, data['id'])
        if not deleted:
            return jsonify({"error": "Not found"}), 404
        
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        # Penyebab paling umum: klasifikasi masih dirujuk arsip surat (foreign key)
        logger.error(f"Gagal menghapus klasifikasi: {e}", exc_info=True)
        return jsonify({"error": "Gagal hapus: Klasifikasi ini sedang digunakan oleh arsip surat."}), 400
    finally:
        db_session.close()

@classification_bp.route('/get_all', methods=['GET'])
def get_all_route() -> ResponseReturnValue:
    """Mengambil klasifikasi per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session: Session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_classifications(db_session, pagination)
        result.items = [r.to_dict() for r in result.items]
        return success_response(result, "Classifications retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar klasifikasi: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally:
        db_session.close()

@classification_bp.route('/get_by_keys', methods=['POST'])
def get_by_keys_route() -> ResponseReturnValue:
    """Mencari klasifikasi.

    Body JSON: `filters` berisi pasangan kolom dan nilai.

    Returns:
        200 dengan klasifikasi yang cocok, atau 400 bila `filters` kosong.
    """
    data = request.json
    filters = data.get('filters')
    if not filters: return jsonify({"error": "Filters required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        results = get_classifications_by_keys(db_session, filters)
        return jsonify([r.to_dict() for r in results]), 200
    finally:
        db_session.close()