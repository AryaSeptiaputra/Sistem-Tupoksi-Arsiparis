import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from app.services.diploma import (
    create_diploma, update_diploma, 
    delete_diploma, get_all_diplomas, get_diplomas_by_keys
)
from app.services.teacher import get_teachers_by_keys
from app.services.log import create_log
from app import db
from app.utils.file_helper import handle_file_upload, delete_physical_file

diploma_bp = Blueprint('diploma', __name__)

def get_current_actor_id(db_session):
    try:
        identity_number = get_jwt_identity()
        teachers = get_teachers_by_keys(db_session, {'identity_number': identity_number})
        return teachers[0].id if teachers else None
    except:
        return None

@diploma_bp.route('/create', methods=['POST'])
@jwt_required()
def create_diploma_route():
    data = request.form.to_dict()
    
    # Konversi Boolean
    if 'is_collected' in data:
        data['is_collected'] = str(data['is_collected']).lower() == 'true'
    
    # Konversi Integer
    if data.get('storage_location_id'):
        try: data['storage_location_id'] = int(data['storage_location_id'])
        except: data['storage_location_id'] = None
    else:
        data['storage_location_id'] = None

    required = ['number', 'student_name', 'major', 'academic_year']
    for f in required:
        if not data.get(f): return jsonify({"error": f"{f} required"}), 400
    
    # File Upload
    file = request.files.get('file')
    if file:
        try:
            path, _ = handle_file_upload(file, 'diplomas')
            data['attachment_path'] = path
        except Exception as e: return jsonify({"error": str(e)}), 500

    db_session: Session = db.SessionLocal()
    try:
        # [UBAH] Create tanpa user_id
        new_diploma = create_diploma(db_session, data)
        
        # Logging
        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Menambah data Ijazah: {new_diploma.student_name}")
            
        return jsonify(new_diploma.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@diploma_bp.route('/update', methods=['POST'])
@jwt_required()
def update_diploma_route():
    data = request.get_json(silent=True) or request.form.to_dict()
    if not data.get('id'): return jsonify({"error": "ID required"}), 400

    if 'is_collected' in data:
        data['is_collected'] = str(data['is_collected']).lower() == 'true'
    
    if 'collected_at' in data and not data['collected_at']:
        data['collected_at'] = None

    if data.get('storage_location_id'):
        try: data['storage_location_id'] = int(data['storage_location_id'])
        except: data['storage_location_id'] = None
    else:
        data['storage_location_id'] = None

    db_session: Session = db.SessionLocal()
    try:
        existing = get_diplomas_by_keys(db_session, {'id': data['id']})
        if not existing: return jsonify({"error": "Not found"}), 404
        old_path = existing[0].attachment_path

        file = request.files.get('file')
        if file:
            try:
                path, _ = handle_file_upload(file, 'diplomas')
                data['attachment_path'] = path
            except Exception as e: return jsonify({"error": str(e)}), 500

        updated = update_diploma(db_session, data['id'], data)

        if file and old_path and old_path != updated.attachment_path:
            delete_physical_file(old_path)

        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Update Ijazah: {updated.student_name}")

        return jsonify(updated.to_dict()), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@diploma_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_diploma_route():
    data = request.json or {}
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_diploma(db_session, data.get('id'))
        if not deleted: return jsonify({"error": "Not found"}), 404

        if deleted.attachment_path:
            delete_physical_file(deleted.attachment_path)

        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Hapus Ijazah: {deleted.student_name}")

        return jsonify(deleted.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@diploma_bp.route('/get_all', methods=['GET'])
def get_all_diplomas_route():
    db_session = db.SessionLocal()
    try: return jsonify([d.to_dict() for d in get_all_diplomas(db_session)]), 200
    finally: db_session.close()

@diploma_bp.route('/get_by_keys', methods=['POST'])
def get_diplomas_by_keys_route():
    data = request.json or {}
    filters = data.get('filters', {})
    db_session = db.SessionLocal()
    try: return jsonify([d.to_dict() for d in get_diplomas_by_keys(db_session, filters)]), 200
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: db_session.close()