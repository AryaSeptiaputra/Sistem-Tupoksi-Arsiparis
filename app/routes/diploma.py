from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from app.errors import FileStorageError
from app.services.diploma import (
    create_diploma, update_diploma,
    delete_diploma, get_all_diplomas, get_diplomas_by_keys
)
from app.services.log import create_log
from app import db
from app.utils.current_user import get_current_user_id
from app.utils.file_helper import handle_file_upload, delete_physical_file
from app.utils.logger import setup_logger
from app.utils.response import handle_database_error
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, error_response

logger = setup_logger(__name__)

diploma_bp = Blueprint('diploma', __name__)

@diploma_bp.route('/create', methods=['POST'])
@jwt_required()
def create_diploma_route() -> ResponseReturnValue:
    """Menambah data ijazah beserta lampiran opsional.

    Form: `number`, `student_name`, `major`, `academic_year`, dan `file` opsional.

    Returns:
        201 dengan data ijazah, 400 bila isian kurang, atau 500 bila
        penyimpanan gagal.
    """
    data = request.form.to_dict()

    if 'is_collected' in data:
        data['is_collected'] = str(data['is_collected']).lower() == 'true'

    if data.get('storage_location_id'):
        try: data['storage_location_id'] = int(data['storage_location_id'])
        except (ValueError, TypeError): data['storage_location_id'] = None
    else:
        data['storage_location_id'] = None

    required = ['number', 'student_name', 'major', 'academic_year']
    for f in required:
        if not data.get(f): return jsonify({"error": f"{f} required"}), 400

    file = request.files.get('file')
    if file:
        try:
            path, _ = handle_file_upload(file, 'diplomas')
            data['attachment_path'] = path
        except (ValueError, FileStorageError) as e: return jsonify({"error": str(e)}), 500

    db_session: Session = db.SessionLocal()
    try:
        new_diploma = create_diploma(db_session, data)

        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Menambah data Ijazah: {new_diploma.student_name}")

        return jsonify(new_diploma.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        return handle_database_error(e, "menyimpan")
    finally:
        db_session.close()

@diploma_bp.route('/update', methods=['POST'])
@jwt_required()
def update_diploma_route() -> ResponseReturnValue:
    """Mengubah data ijazah dan lampirannya.

    Form atau JSON: `id`, kolom yang diubah, `file` atau `remove_attachment`.

    Returns:
        200 dengan data ijazah, 400 bila `id` kosong, 404 bila tidak
        ditemukan, atau 500 bila penyimpanan gagal.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data.get('id'): return jsonify({"error": "ID required"}), 400

    if 'is_collected' in data:
        data['is_collected'] = str(data['is_collected']).lower() == 'true'

    if 'collected_at' in data and not data['collected_at']:
        data['collected_at'] = None

    if data.get('storage_location_id'):
        try: data['storage_location_id'] = int(data['storage_location_id'])
        except (ValueError, TypeError): data['storage_location_id'] = None
    else:
        data['storage_location_id'] = None

    db_session: Session = db.SessionLocal()
    try:
        existing = get_diplomas_by_keys(db_session, {'id': data['id']})
        if not existing: return jsonify({"error": "Not found"}), 404
        old_path = existing[0].attachment_path

        file = request.files.get('file')
        remove_attachment = data.get('remove_attachment', 'false').lower() == 'true'

        if file:
            try:
                path, _ = handle_file_upload(file, 'diplomas')
                data['attachment_path'] = path
            except (ValueError, FileStorageError) as e: return jsonify({"error": str(e)}), 500
        elif remove_attachment:
            # Lampiran dilepas tanpa diganti file baru
            data['attachment_path'] = None
        # Tanpa file baru dan tanpa remove_attachment, attachment_path tidak diubah

        updated = update_diploma(db_session, data['id'], data)

        # File lama dihapus hanya bila lampiran diganti atau dilepas
        if old_path and (file or remove_attachment) and old_path != updated.attachment_path:
            delete_physical_file(old_path)

        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Update Ijazah: {updated.student_name}")

        return jsonify(updated.to_dict()), 200
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e, "memperbarui")
    finally:
        db_session.close()

@diploma_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_diploma_route() -> ResponseReturnValue:
    """Menghapus data ijazah beserta file lampirannya.

    Body JSON: `id`.

    Returns:
        200 dengan data yang dihapus, 404 bila tidak ditemukan, atau 500
        bila terjadi error.
    """
    data = request.json or {}
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_diploma(db_session, data.get('id'))
        if not deleted: return jsonify({"error": "Not found"}), 404

        if deleted.attachment_path:
            delete_physical_file(deleted.attachment_path)

        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Hapus Ijazah: {deleted.student_name}")

        return jsonify(deleted.to_dict()), 200
    except Exception as e:
        logger.error(f"Gagal menghapus ijazah: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@diploma_bp.route('/get_all', methods=['GET'])
def get_all_diplomas_route() -> ResponseReturnValue:
    """Mengambil data ijazah per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_diplomas(db_session, pagination)
        result.items = [d.to_dict() for d in result.items]
        return success_response(result, "Diplomas retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar ijazah: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally: db_session.close()

@diploma_bp.route('/get_by_keys', methods=['POST'])
def get_diplomas_by_keys_route() -> ResponseReturnValue:
    """Mencari data ijazah.

    Body JSON: `filters` berisi pasangan kolom dan nilai.

    Returns:
        200 dengan ijazah yang cocok, atau 400 bila terjadi error.
    """
    data = request.json or {}
    filters = data.get('filters', {})
    db_session = db.SessionLocal()
    try: return jsonify([d.to_dict() for d in get_diplomas_by_keys(db_session, filters)]), 200
    except Exception as e:
        logger.error(f"Gagal mencari ijazah: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400
    finally: db_session.close()
