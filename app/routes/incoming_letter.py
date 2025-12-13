import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from app.services.incoming_letter import (
    create_incoming_letter, update_incoming_letter, 
    delete_incoming_letter, get_all_incoming_letters, 
    get_incoming_letters_by_keys
)
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db
from app.utils.file_helper import handle_file_upload, delete_physical_file

incoming_letter_bp = Blueprint('incoming_letter', __name__)

def get_current_user_obj(db_session):
    current_nuptk = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_nuptk})
    return users[0] if users else None

@incoming_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_incoming_letter_route():
    data = request.form.to_dict()
    required_fields = ['number', 'letter_date', 'received_date', 'sender', 'classification_id']
    
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
            
    # Handle File
    file = request.files.get('file')
    attachment_path, full_path = None, None
    if file:
        try:
            attachment_path, full_path = handle_file_upload(file, 'incoming_letters')
            data['attachment_path'] = attachment_path
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    
    # Handle optional storage_location_id
    if not data.get('storage_location_id'):
        data['storage_location_id'] = None
    
    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            if full_path and os.path.exists(full_path): os.remove(full_path)
            return jsonify({"error": "User authentication failed"}), 401
        
        new_letter = create_incoming_letter(db_session, data, user_id=current_user.id)
        create_log(db_session, current_user.id, f"Tambah surat masuk No: '{new_letter.number}'")
        return jsonify(new_letter.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        if full_path and os.path.exists(full_path): os.remove(full_path)
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@incoming_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_incoming_letter_route():
    # Support both JSON and Form Data
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    letter_id = data.get('id')
    
    if not letter_id: return jsonify({"error": "ID wajib ada"}), 400

    # Type Conversion
    if data.get('classification_id'):
        try: data['classification_id'] = int(data['classification_id'])
        except: return jsonify({"error": "Invalid classification_id"}), 400
        
    if data.get('storage_location_id'):
        try: data['storage_location_id'] = int(data['storage_location_id'])
        except: data['storage_location_id'] = None # Handle "Select..." value

    db_session: Session = db.SessionLocal()
    try:
        existing = get_incoming_letters_by_keys(db_session, {'id': letter_id})
        if not existing: return jsonify({"error": "Letter not found"}), 404
        old_path = existing[0].attachment_path

        # Handle File Upload
        file = request.files.get('file')
        if file:
            try:
                attachment_path, _ = handle_file_upload(file, 'incoming_letters')
                data['attachment_path'] = attachment_path
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        updated_letter = update_incoming_letter(db_session, letter_id, data)

        # Cleanup old file
        if file and old_path and old_path != updated_letter.attachment_path:
            delete_physical_file(old_path)

        current_user = get_current_user_obj(db_session)
        if current_user:
            create_log(db_session, current_user.id, f"Update surat masuk No: '{updated_letter.number}'")

        return jsonify(updated_letter.to_dict()), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@incoming_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_incoming_letter_route():
    data = request.json or {}
    letter_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_letter = delete_incoming_letter(db_session, letter_id)
        if not deleted_letter: return jsonify({"error": "Not found"}), 404

        if deleted_letter.attachment_path:
            delete_physical_file(deleted_letter.attachment_path)

        current_user = get_current_user_obj(db_session)
        if current_user:
            create_log(db_session, current_user.id, f"Hapus surat masuk No: '{deleted_letter.number}'")

        return jsonify(deleted_letter.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@incoming_letter_bp.route('/get_all', methods=['GET'])
def get_all_incoming_letters_route():
    db_session = db.SessionLocal()
    try: return jsonify([l.to_dict() for l in get_all_incoming_letters(db_session)]), 200
    finally: db_session.close()

@incoming_letter_bp.route('/get_by_keys', methods=['POST'])
def get_incoming_by_keys_route():
    data = request.json or {}
    filters = data.get('filters')
    if not filters: return jsonify({"error": "filters required"}), 400
    db_session = db.SessionLocal()
    try: return jsonify([l.to_dict() for l in get_incoming_letters_by_keys(db_session, filters)]), 200
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: db_session.close()