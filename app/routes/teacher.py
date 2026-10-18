from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.services.teacher import create_teacher, update_teacher, delete_teacher, get_all_teachers, get_teachers_by_keys
from app.services.log import create_log
from app.utils.current_user import get_current_user_id
from app import db
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, error_response
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/create', methods=['POST'])
@jwt_required()
def create_teacher_route() -> ResponseReturnValue:
    """Menambah data guru atau pegawai.

    Body JSON: `identity_number`, `full_name`, `gender`,
    `employment_status`, `status`, serta `rank` dan `address` opsional.

    Returns:
        201 bila tersimpan, 400 bila isian kurang, 409 bila NIP/NUPTK sudah
        terdaftar, atau 500 bila terjadi error.
    """
    data = request.json
    required_fields = ['identity_number', 'full_name', 'gender', 'employment_status', 'status']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()

    try:
        new_teacher = create_teacher(db_session, data)
        
        try:
            action = f"Menambahkan Guru/Pegawai baru: '{new_teacher.full_name}' ({new_teacher.identity_number})."
            create_log(db_session, get_current_user_id(), action)
        except SQLAlchemyError as e:
            logger.warning(f"Gagal mencatat log tambah guru: {e}", exc_info=True)

        return jsonify({
            "message": f"Berhasil menambahkan data guru: {new_teacher.full_name}"
        }), 201
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"message": "NIP/NUPTK sudah terdaftar."}), 409
    except Exception as e:
        db_session.rollback()
        logger.error(f"Gagal menambah guru: {e}", exc_info=True)
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        db_session.close()

@teacher_bp.route('/update', methods=['POST'])
@jwt_required()
def update_teacher_route() -> ResponseReturnValue:
    """Mengubah data guru.

    Body JSON: `id` dan kolom yang diubah.

    Returns:
        200 bila tersimpan, 400 bila `id` kosong, 404 bila tidak ditemukan,
        atau 409 bila NIP/NUPTK bentrok.
    """
    data = request.json
    teacher_id = data.get('id')
    
    if not teacher_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated = update_teacher(db_session, teacher_id, data)
        if not updated:
            return jsonify({"error": "Teacher not found"}), 404
        
        try:
            create_log(db_session, get_current_user_id(), f"Memperbarui data guru: {updated.full_name}")
        except SQLAlchemyError as e:
            logger.warning(f"Gagal mencatat log ubah guru: {e}", exc_info=True)

        return jsonify({"message": "Data berhasil diperbarui"}), 200

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "NIP/NUPTK conflict"}), 409
    finally:
        db_session.close()

@teacher_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_teacher_route() -> ResponseReturnValue:
    """Menghapus data guru beserta arsip pegawainya.

    Body JSON: `id`.

    Returns:
        200 bila terhapus, 400 bila `id` kosong, 404 bila tidak ditemukan,
        atau 500 bila terjadi error.
    """
    data = request.json
    teacher_id = data.get('id')
    
    if not teacher_id:
        return jsonify({"error": "id is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_teacher(db_session, teacher_id)
        if not deleted:
            return jsonify({"error": "Teacher not found"}), 404
        
        try:
            create_log(db_session, get_current_user_id(), f"Menghapus data guru: {deleted.full_name}")
        except SQLAlchemyError as e:
            logger.warning(f"Gagal mencatat log hapus guru: {e}", exc_info=True)

        return jsonify({"message": "Data berhasil dihapus"}), 200
    except Exception as e:
        logger.error(f"Gagal menghapus guru: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@teacher_bp.route('/get_all', methods=['GET'])
def get_all_teachers_route() -> ResponseReturnValue:
    """Mengambil data guru per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session: Session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_teachers(db_session, pagination)
        result.items = [t.to_dict() for t in result.items]
        return success_response(result, "Teachers retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar guru: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally:
        db_session.close()

@teacher_bp.route('/get_by_keys', methods=['POST'])
def get_teachers_by_keys_route() -> ResponseReturnValue:
    """Mencari data guru.

    Body JSON: `filters` berisi pasangan kolom dan nilai.

    Returns:
        200 dengan data yang cocok, atau 400 bila `filters` bukan dict.
    """
    data = request.json
    filters = data.get('filters')
    
    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        teachers = get_teachers_by_keys(db_session, filters)
        return jsonify([t.to_dict() for t in teachers]), 200
    finally:
        db_session.close()