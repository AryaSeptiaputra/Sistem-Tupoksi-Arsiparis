import os
from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from app.services.outgoing_letter import (
    create_outgoing_letter, update_outgoing_letter, 
    delete_outgoing_letter, get_all_outgoing_letters, 
    get_outgoing_letters_by_keys
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

outgoing_letter_bp = Blueprint('outgoing_letter', __name__)

@outgoing_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_outgoing_letter_route() -> ResponseReturnValue:
    """Menambah surat keluar beserta lampiran opsional.

    Form: `number`, `letter_date`, `sent_date`, `destination`,
    `classification_id`, kolom lain, dan `file` opsional.

    Returns:
        201 dengan data surat, 400 bila isian kurang atau id bukan angka,
        atau 500 bila penyimpanan gagal.
    """
    data = request.form.to_dict()
    
    if 'is_decree' in data:
        data['is_decree'] = str(data['is_decree']).lower() == 'true'
    else:
        data['is_decree'] = False

    try:
        if 'classification_id' in data and data['classification_id']:
            data['classification_id'] = int(data['classification_id'])
        else:
             return jsonify({"error": "Classification ID is required"}), 400

        if 'storage_location_id' in data and data['storage_location_id']:
            data['storage_location_id'] = int(data['storage_location_id'])
        else:
            data['storage_location_id'] = None

    except ValueError:
            return jsonify({"error": "ID Klasifikasi/Lokasi harus berupa angka"}), 400

    field_labels = {
        'number': 'Nomor Surat',
        'letter_date': 'Tanggal Surat',
        'sent_date': 'Tanggal Kirim',
        'destination': 'Tujuan'
    }
    
    for field, label in field_labels.items():
        if not data.get(field):
            return jsonify({"error": f"{label} wajib diisi"}), 400
    
    file = request.files.get('file')
    attachment_path = None
    if file:
        try:
            attachment_path, _ = handle_file_upload(file, 'outgoing_letters')
            data['attachment_path'] = attachment_path
        except (ValueError, FileStorageError) as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    db_session: Session = db.SessionLocal()
    try:
        new_letter = create_outgoing_letter(db_session, data)
        
        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Menambahkan surat keluar No: '{new_letter.number}'")
            
        return jsonify(new_letter.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        return handle_database_error(e, "menyimpan")
    finally:
        db_session.close()

@outgoing_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_outgoing_letter_route() -> ResponseReturnValue:
    """Mengubah surat keluar dan lampirannya.

    Form atau JSON: `id`, kolom yang diubah, `file` atau `remove_attachment`.

    Returns:
        200 dengan data surat, 400 bila `id` kosong atau id bukan angka, 404
        bila tidak ditemukan, atau 500 bila penyimpanan gagal.
    """
    data = request.get_json(silent=True) or request.form.to_dict()
    letter_id = data.get('id')
    
    if not letter_id: return jsonify({"error": "ID surat wajib ada"}), 400

    if 'is_decree' in data:
        data['is_decree'] = str(data['is_decree']).lower() == 'true'
    
    try:
        if 'classification_id' in data:
            data['classification_id'] = int(data['classification_id'])
        
        if 'storage_location_id' in data:
            if data['storage_location_id']:
                data['storage_location_id'] = int(data['storage_location_id'])
            else:
                data['storage_location_id'] = None
    except ValueError:
        return jsonify({"error": "ID harus berupa angka"}), 400

    db_session: Session = db.SessionLocal()
    try:
        existing_letters = get_outgoing_letters_by_keys(db_session, {'id': letter_id})
        if not existing_letters: return jsonify({"error": "Letter not found"}), 404
        
        old_file_path = existing_letters[0].attachment_path 

        file = request.files.get('file')
        remove_attachment = data.get('remove_attachment', 'false').lower() == 'true'
        
        if file:
            try:
                attachment_path, _ = handle_file_upload(file, 'outgoing_letters')
                data['attachment_path'] = attachment_path
            except (ValueError, FileStorageError) as e:
                return jsonify({"error": f"Gagal upload file: {str(e)}"}), 500
        elif remove_attachment:
            # Lampiran dilepas tanpa diganti file baru
            data['attachment_path'] = None
        # Tanpa file baru dan tanpa remove_attachment, attachment_path tidak diubah
        
        updated_letter = update_outgoing_letter(db_session, letter_id, data)
        
        # File lama dihapus hanya bila lampiran diganti atau dilepas
        if old_file_path and (file or remove_attachment) and old_file_path != updated_letter.attachment_path:
            delete_physical_file(old_file_path)

        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Update surat keluar No: '{updated_letter.number}'")

        return jsonify(updated_letter.to_dict()), 200

    except Exception as e:
        db_session.rollback()
        return handle_database_error(e, "memperbarui")
    finally:
        db_session.close()

@outgoing_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_outgoing_letter_route() -> ResponseReturnValue:
    """Menghapus surat keluar beserta file lampirannya.

    Body JSON: `id`.

    Returns:
        200 dengan data yang dihapus, 404 bila tidak ditemukan, atau 500
        bila terjadi error.
    """
    data = request.json or {}
    letter_id = data.get('id')

    db_session: Session = db.SessionLocal()
    try:
        deleted_letter = delete_outgoing_letter(db_session, letter_id)
        if not deleted_letter: return jsonify({"error": "Letter not found"}), 404

        if deleted_letter.attachment_path:
            delete_physical_file(deleted_letter.attachment_path)

        actor_id = get_current_user_id()
        if actor_id:
            create_log(db_session, actor_id, f"Hapus surat keluar No: '{deleted_letter.number}'")

        return jsonify(deleted_letter.to_dict()), 200
    except Exception as e:
        logger.error(f"Gagal menghapus surat keluar: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_all', methods=['GET'])
def get_all_outgoing_letters_route() -> ResponseReturnValue:
    """Mengambil surat keluar per halaman.

    Query: `page`, `per_page`, `sort_by`, `sort_order`.

    Returns:
        200 dengan satu halaman data, atau 500 bila terjadi error.
    """
    db_session = db.SessionLocal()
    try:
        pagination = get_pagination_params(request.args)
        result = get_all_outgoing_letters(db_session, pagination)
        result.items = [l.to_dict() for l in result.items]
        return success_response(result, "Outgoing letters retrieved successfully", 200)
    except Exception as e:
        logger.error(f"Gagal mengambil daftar surat keluar: {e}", exc_info=True)
        return error_response(str(e), 500)
    finally: db_session.close()

@outgoing_letter_bp.route('/get_by_keys', methods=['POST'])
def get_outgoing_by_keys_route() -> ResponseReturnValue:
    """Mencari surat keluar.

    Body JSON: `filters` berisi pasangan kolom dan nilai.

    Returns:
        200 dengan surat yang cocok, atau 400 bila `filters` kosong atau
        terjadi error.
    """
    data = request.json or {}
    filters = data.get('filters')
    if not filters: return jsonify({"error": "filters required"}), 400
    db_session = db.SessionLocal()
    try: return jsonify([l.to_dict() for l in get_outgoing_letters_by_keys(db_session, filters)]), 200
    except Exception as e:
        logger.error(f"Gagal mencari surat keluar: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 400
    finally: db_session.close()