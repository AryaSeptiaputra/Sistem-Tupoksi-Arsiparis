import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from app.services.outgoing_letter import (
    create_outgoing_letter, update_outgoing_letter, 
    delete_outgoing_letter, get_all_outgoing_letters, 
    get_outgoing_letters_paginated, get_outgoing_letters_by_keys
)
from app.services.teacher import get_teachers_by_keys
from app.services.log import create_log
from app import db
from app.utils.file_helper import handle_file_upload, delete_physical_file

outgoing_letter_bp = Blueprint('outgoing_letter', __name__)

def get_current_actor_id(db_session):
    """Helper untuk mendapatkan ID Teacher dari user yang login (untuk logging)"""
    try:
        identity_number = get_jwt_identity()
        teachers = get_teachers_by_keys(db_session, {'identity_number': identity_number})
        return teachers[0].id if teachers else None
    except:
        return None

@outgoing_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_outgoing_letter_route():
    data = request.form.to_dict()
    
    # Validasi Boolean
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

    required_fields = ['number', 'letter_date', 'sent_date', 'destination']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    
    # File Upload
    file = request.files.get('file')
    attachment_path = None
    if file:
        try:
            attachment_path, _ = handle_file_upload(file, 'outgoing_letters')
            data['attachment_path'] = attachment_path
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    db_session: Session = db.SessionLocal()
    try:
        # [UBAH] Hapus user_id
        new_letter = create_outgoing_letter(db_session, data)
        
        # Logging
        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Menambahkan surat keluar No: '{new_letter.number}'")
            
        return jsonify(new_letter.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_outgoing_letter_route():
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
        if file:
            try:
                attachment_path, _ = handle_file_upload(file, 'outgoing_letters')
                data['attachment_path'] = attachment_path
            except Exception as e:
                return jsonify({"error": f"Gagal upload file: {str(e)}"}), 500
        
        updated_letter = update_outgoing_letter(db_session, letter_id, data)
        
        if file and old_file_path and old_file_path != updated_letter.attachment_path:
            delete_physical_file(old_file_path)

        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Update surat keluar No: '{updated_letter.number}'")

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
        if not deleted_letter: return jsonify({"error": "Letter not found"}), 404

        if deleted_letter.attachment_path:
            delete_physical_file(deleted_letter.attachment_path)

        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Hapus surat keluar No: '{deleted_letter.number}'")

        return jsonify(deleted_letter.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_all', methods=['GET'])
def get_all_outgoing_letters_route():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({"error": "Invalid page or per_page parameters"}), 400
    except ValueError:
        return jsonify({"error": "Page and per_page must be integers"}), 400
    
    db_session = db.SessionLocal()
    try:
        result = get_outgoing_letters_paginated(db_session, page=page, per_page=per_page)
        return jsonify({
            'outgoing_letters': [l.to_dict() for l in result['outgoing_letters']],
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages']
            }
        }), 200
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_by_keys', methods=['POST'])
def get_outgoing_by_keys_route():
    data = request.json or {}
    filters = data.get('filters')
    if not filters: return jsonify({"error": "filters required"}), 400
    db_session = db.SessionLocal()
    try: return jsonify([l.to_dict() for l in get_outgoing_letters_by_keys(db_session, filters)]), 200
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: db_session.close()