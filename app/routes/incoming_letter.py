import os
from flask import Blueprint, request
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session

from app.services.incoming_letter import (
    create_incoming_letter, update_incoming_letter, 
    delete_incoming_letter, get_all_incoming_letters, 
    get_incoming_letters_by_keys
)
from app.services.log import create_log
from app import db
from app.errors import FileStorageError
from app.utils.current_user import get_current_user_id
from app.utils.file_helper import handle_file_upload, delete_physical_file
from app.utils.logger import setup_logger
from app.utils.pagination import get_pagination_params
from app.utils.response import success_response, error_response, handle_database_error

logger = setup_logger(__name__)

incoming_letter_bp = Blueprint('incoming_letter', __name__)

@incoming_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_incoming_letter_route() -> ResponseReturnValue:
    """Menambah surat masuk beserta lampiran opsional.

    Form: `number`, `letter_date`, `received_date`, `sender`,
    `classification_id`, kolom lain, dan `file` opsional.

    Returns:
        201 dengan data surat, 400 bila isian kurang, atau 500 bila
        penyimpanan gagal.
    """
    data = request.form.to_dict()
    
    field_labels = {
        'number': 'Nomor Surat',
        'letter_date': 'Tanggal Surat',
        'received_date': 'Tanggal Diterima',
        'sender': 'Pengirim',
        'classification_id': 'Klasifikasi'
    }
    
    for field, label in field_labels.items():
        if not data.get(field):
            return error_response(f"{label} wajib diisi", 400)
            
    file = request.files.get('file')
    attachment_path, full_path = None, None
    if file:
        try:
            attachment_path, full_path = handle_file_upload(file, 'incoming_letters')
            data['attachment_path'] = attachment_path
        except (ValueError, FileStorageError) as e:
            return error_response(f"Failed to save file: {str(e)}", 500)
    
    if not data.get('storage_location_id'):
        data['storage_location_id'] = None
    
    db_session: Session = db.SessionLocal()
    try:
        new_letter = create_incoming_letter(db_session, data)

        create_log(db_session, get_current_user_id(), f"Tambah surat masuk No: '{new_letter.number}'")
        return success_response(new_letter.to_dict(), "Incoming letter created successfully", 201)

    except Exception as e:
        db_session.rollback()
        if full_path and os.path.exists(full_path): os.remove(full_path)
        return handle_database_error(e, "menyimpan")
    finally:
        db_session.close()

@incoming_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_incoming_letter_route() -> ResponseReturnValue:
    """Mengubah surat masuk dan lampirannya.

    Form atau JSON: `id`, kolom yang diubah, `file` atau `remove_attachment`.

    Returns:
        200 dengan data surat, 400 bila `id` kosong atau tidak valid, 404
        bila tidak ditemukan, atau 500 bila penyimpanan gagal.
    """
    # Menerima JSON maupun form data
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    letter_id = data.get('id')
    
    if not letter_id: return error_response("ID wajib ada", 400)

    if data.get('classification_id'):
        try: data['classification_id'] = int(data['classification_id'])
        except (ValueError, TypeError): return error_response("Invalid classification_id", 400)

    if data.get('storage_location_id'):
        try: data['storage_location_id'] = int(data['storage_location_id'])
        except (ValueError, TypeError): data['storage_location_id'] = None # Handle "Select..." value

    db_session: Session = db.SessionLocal()
    try:
        existing = get_incoming_letters_by_keys(db_session, {'id': letter_id})
        if not existing: return error_response("Letter not found", 404)
        old_path = existing[0].attachment_path

        file = request.files.get('file')
        remove_attachment = data.get('remove_attachment', 'false').lower() == 'true'
        
        if file:
            try:
                attachment_path, _ = handle_file_upload(file, 'incoming_letters')
                data['attachment_path'] = attachment_path
            except (ValueError, FileStorageError) as e:
                return error_response(str(e), 500)
        elif remove_attachment:
            # Lampiran dilepas tanpa diganti file baru
            data['attachment_path'] = None
        # Tanpa file baru dan tanpa remove_attachment, attachment_path tidak diubah

        updated_letter = update_incoming_letter(db_session, letter_id, data)

        # File lama dihapus hanya bila lampiran diganti atau dilepas
        if old_path and (file or remove_attachment) and old_path != updated_letter.attachment_path:
            delete_physical_file(old_path)

        create_log(db_session, get_current_user_id(), f"Update surat masuk No: '{updated_letter.number}'")

        return success_response(updated_letter.to_dict(), "Incoming letter updated successfully", 200)
    except Exception as e:
        db_session.rollback()
        return handle_database_error(e, "memperbarui")
    finally:
        db_session.close()

@incoming_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_incoming_letter_route() -> ResponseReturnValue:
    """Menghapus surat masuk beserta file lampirannya.

    Body JSON: `id`.

    Returns:
        200 dengan data yang dihapus, 404 bila tidak ditemukan, atau 500
        bila terjadi error.
    """
    data = request.json or {}
    letter_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_letter = delete_incoming_letter(db_session, letter_id)
        if not deleted_letter: return error_response("Not found", 404)

        if deleted_letter.attachment_path:
            delete_physical_file(deleted_letter.attachment_path)

        create_log(db_session, get_current_user_id(), f"Hapus surat masuk No: '{deleted_letter.number}'")

        return success_response(deleted_letter.to_dict(), "Incoming letter deleted successfully", 200)
    except Exception as e:
        logger.error(f"Gagal menghapus surat masuk: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally:
        db_session.close()

@incoming_letter_bp.route('/get_all', methods=['GET'])
def get_all_incoming_letters_route() -> ResponseReturnValue:
    """Mengambil surat masuk per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_incoming_letters(db_session, pagination)
        return success_response(result, "Incoming letters retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar surat masuk: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally:
        db_session.close()

@incoming_letter_bp.route('/get_by_keys', methods=['POST'])
def get_incoming_by_keys_route() -> ResponseReturnValue:
    """Mencari surat masuk per halaman.

    Body JSON: `filters` (misalnya `number`, `sender`, `classification_id`,
    `archive_status`), `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman hasil, atau 500 bila terjadi error.
    """
    data = request.json or {}
    filters = data.get('filters', {})
    
    db_session = db.SessionLocal()
    try:
        page = data.get('page') or request.args.get('page', 1, type=int)
        per_page = data.get('per_page') or request.args.get('per_page', 20, type=int)
        
        pagination = get_pagination_params({
            'page': page,
            'per_page': per_page,
            'sort_by': data.get('sort_by', 'id'),
            'sort_order': data.get('sort_order', 'desc')
        })
        
        result = get_incoming_letters_by_keys(db_session, filters, pagination)
        return success_response(result, "Incoming letters retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mencari surat masuk: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally:
        db_session.close()
