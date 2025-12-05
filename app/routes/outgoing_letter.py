import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

# Import Services
from app.services.outgoing_letter import (
    create_outgoing_letter, update_outgoing_letter, 
    delete_outgoing_letter, get_all_outgoing_letters, 
    get_outgoing_letters_by_keys
)
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db

# Import Helper (Sesuaikan path import Anda)
from app.utils.file_helper import handle_file_upload, delete_physical_file

outgoing_letter_bp = Blueprint('outgoing_letter', __name__)

def get_current_user_obj(db_session: Session):
    current_nuptk = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_nuptk})
    return users[0] if users else None

@outgoing_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_outgoing_letter_route():
    data = request.form.to_dict()
    
    # Validasi & Konversi
    if 'is_decree' in data:
        data['is_decree'] = data['is_decree'].lower() == 'true'
    
    try:
        if 'classification_id' in data:
            data['classification_id'] = int(data['classification_id'])
    except ValueError:
            return jsonify({"error": "Classification ID harus angka"}), 400

    required_fields = ['number', 'letter_date', 'sent_date', 'destination', 'classification_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    
    # --- OPTIMIZED UPLOAD ---
    file = request.files.get('file')
    attachment_path, full_path = None, None
    
    if file:
        try:
            attachment_path, full_path = handle_file_upload(file, 'outgoing_letters')
            data['attachment_path'] = attachment_path
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            # Rollback file jika auth gagal
            if full_path and os.path.exists(full_path): os.remove(full_path)
            return jsonify({"error": "User authentication failed"}), 401

        new_letter = create_outgoing_letter(db_session, data, user_id=current_user.id)
        
        create_log(db_session, current_user.id, f"Menambahkan surat keluar No: '{new_letter.number}'")
        return jsonify(new_letter.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        # Rollback file jika DB gagal
        if full_path and os.path.exists(full_path): os.remove(full_path)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_outgoing_letter_route():
    data = request.get_json(silent=True) or request.form.to_dict()
    letter_id = data.get('id')
    
    if not letter_id:
        return jsonify({"error": "ID surat wajib ada"}), 400

    # Konversi data...
    if 'is_decree' in data:
        data['is_decree'] = str(data['is_decree']).lower() == 'true'
    if 'classification_id' in data:
        try: data['classification_id'] = int(data['classification_id'])
        except: return jsonify({"error": "Classification ID invalid"}), 400

    db_session: Session = db.SessionLocal()
    try:
        # Ambil data lama untuk cek file lama (Optimisasi Storage)
        existing_letters = get_outgoing_letters_by_keys(db_session, {'id': letter_id})
        old_file_path = existing_letters[0].attachment_path if existing_letters else None

        # --- OPTIMIZED UPLOAD ---
        file = request.files.get('file')
        if file:
            try:
                attachment_path, _ = handle_file_upload(file, 'outgoing_letters')
                data['attachment_path'] = attachment_path
            except Exception as e:
                return jsonify({"error": f"Gagal upload file: {str(e)}"}), 500
        
        updated_letter = update_outgoing_letter(db_session, letter_id, data)
        if not updated_letter:
            return jsonify({"error": "Letter not found"}), 404
        
        # Jika sukses update & ada file baru, hapus file lama
        if file and old_file_path and old_file_path != updated_letter.attachment_path:
            delete_physical_file(old_file_path)

        current_user = get_current_user_obj(db_session)
        if current_user:
            create_log(db_session, current_user.id, f"Update surat keluar No: '{updated_letter.number}'")

        return jsonify(updated_letter.to_dict()), 200

    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_outgoing_letter_route():
    data = request.json or {}
    letter_id = data.get('id')

    db_session: Session = db.SessionLocal()
    try:
        deleted_letter = delete_outgoing_letter(db_session, letter_id)
        if not deleted_letter:
            return jsonify({"error": "Letter not found"}), 404

        # --- FITUR DELETE FISIK ---
        if deleted_letter.attachment_path:
            delete_physical_file(deleted_letter.attachment_path)

        current_user = get_current_user_obj(db_session)
        if current_user:
            create_log(db_session, current_user.id, f"Hapus surat keluar No: '{deleted_letter.number}'")

        return jsonify(deleted_letter.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

# (Route get_all dan get_by_keys tetap sama, tidak perlu diubah)
@outgoing_letter_bp.route('/get_all', methods=['GET'])
def get_all_outgoing_letters_route():
    db_session = db.SessionLocal()
    try:
        return jsonify([l.to_dict() for l in get_all_outgoing_letters(db_session)]), 200
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_by_keys', methods=['POST'])
def get_outgoing_by_keys_route():
    data = request.json or {}
    filters = data.get('filters')
    if not filters: return jsonify({"error": "filters required"}), 400
    db_session = db.SessionLocal()
    try:
        return jsonify([l.to_dict() for l in get_outgoing_letters_by_keys(db_session, filters)]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()