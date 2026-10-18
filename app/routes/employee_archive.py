from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required

from app.models.employee_archive import EmployeeArchive
from app.services.employee_archive import (
    create_employee_archive, update_employee_archive, 
    delete_employee_archive, get_all_employee_archives
)
from app.services.log import create_log
from app import db
from app.errors import FileStorageError
from app.utils.current_user import get_current_user_id
from app.utils.file_helper import handle_file_upload, delete_physical_file
from app.utils.logger import setup_logger
from app.utils.response import handle_database_error
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, error_response

logger = setup_logger(__name__)

employee_archive_bp = Blueprint('employee_archive', __name__)

@employee_archive_bp.route('/create', methods=['POST'])
@jwt_required()
def create_route() -> ResponseReturnValue:
    """Menambah arsip pegawai beserta lampiran opsional.

    Form: `document_name`, `owner_id`, kolom lain, dan `file` opsional.

    Returns:
        201 dengan data arsip, 400 bila isian kurang, atau 500 bila
        penyimpanan gagal.
    """
    data = request.form.to_dict()
    
    if not data.get('document_name') or not data.get('owner_id'):
        return jsonify({"error": "Nama Dokumen dan Pemilik wajib diisi"}), 400
        
    file = request.files.get('file')
    if file:
        try:
            path, _ = handle_file_upload(file, 'employee_archives')
            data['attachment_path'] = path
        except (ValueError, FileStorageError) as e:
            return jsonify({"error": str(e)}), 500
    
    db_session = db.SessionLocal()
    try:
        new_data = create_employee_archive(db_session, data)
        
        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Upload Arsip Pegawai: {new_data.document_name}")
        
        return jsonify(new_data.to_dict()), 201
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e, "menyimpan")
    finally:
        db_session.close()

@employee_archive_bp.route('/update', methods=['POST'])
@jwt_required()
def update_route() -> ResponseReturnValue:
    """Mengubah arsip pegawai dan lampirannya.

    Form: `id`, kolom yang diubah, `file` atau `remove_attachment`.

    Returns:
        200 dengan data arsip, 400 bila `id` kosong, 404 bila tidak
        ditemukan, atau 500 bila penyimpanan gagal.
    """
    data = request.form.to_dict()
    if not data.get('id'): return jsonify({"error": "ID required"}), 400

    db_session = db.SessionLocal()
    try:
        curr = db_session.query(EmployeeArchive).filter(EmployeeArchive.id == data.get('id')).first()
        if not curr: return jsonify({"error": "Not found"}), 404
        old_path = curr.attachment_path

        file = request.files.get('file')
        remove_attachment = data.get('remove_attachment', 'false').lower() == 'true'
        
        if file:
            try:
                path, _ = handle_file_upload(file, 'employee_archives')
                data['attachment_path'] = path
            except (ValueError, FileStorageError) as e: return jsonify({"error": str(e)}), 500
        elif remove_attachment:
            # Lampiran dilepas tanpa diganti file baru
            data['attachment_path'] = None
        # Tanpa file baru dan tanpa remove_attachment, attachment_path tidak diubah

        updated = update_employee_archive(db_session, data.get('id'), data)
        
        # File lama dihapus hanya bila lampiran diganti atau dilepas
        if old_path and (file or remove_attachment) and old_path != updated.attachment_path:
            delete_physical_file(old_path)
        
        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Update Arsip Pegawai: {updated.document_name}")

        return jsonify(updated.to_dict()), 200
    except Exception as e:
        return handle_database_error(e, "memperbarui")
    finally:
        db_session.close()

@employee_archive_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_route() -> ResponseReturnValue:
    """Menghapus arsip pegawai beserta file lampirannya.

    Body JSON: `id`.

    Returns:
        200 bila terhapus, 404 bila tidak ditemukan, atau 500 bila terjadi error.
    """
    data = request.json or {}
    db_session = db.SessionLocal()
    try:
        deleted = delete_employee_archive(db_session, data.get('id'))
        if deleted:
            if deleted.attachment_path: delete_physical_file(deleted.attachment_path)
            actor_id = get_current_user_id()
            if actor_id: create_log(db_session, actor_id, f"Hapus Arsip Pegawai: {deleted.document_name}")
            return jsonify({"status": "deleted"}), 200
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        logger.error(f"Gagal menghapus arsip pegawai: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@employee_archive_bp.route('/get_all', methods=['GET'])
def get_all_route() -> ResponseReturnValue:
    """Mengambil arsip pegawai per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_employee_archives(db_session, pagination)
        result.items = [x.to_dict() for x in result.items]
        return success_response(result, "Employee archives retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar arsip pegawai: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally: db_session.close()