import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from app.services.diploma import (
    create_diploma, update_diploma, 
    delete_diploma, get_all_diplomas, 
    get_diplomas_by_keys
)
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db
from app.utils.file_helper import handle_file_upload, delete_physical_file

diploma_bp = Blueprint('diploma', __name__)

def get_current_user_obj(db_session):
    current = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current})
    return users[0] if users else None

@diploma_bp.route('/create', methods=['POST'])
@jwt_required()
def create_diploma_route():
    data = request.form.to_dict()
    if 'is_collected' in data:
        data['is_collected'] = str(data['is_collected']).lower() == 'true'

    required = ['number', 'student_name', 'major', 'academic_year']
    for f in required:
        if not data.get(f): return jsonify({"error": f"{f} required"}), 400
    
    # --- OPTIMIZED UPLOAD ---
    file = request.files.get('file')
    path, full_path = None, None
    if file:
        try:
            path, full_path = handle_file_upload(file, 'diplomas')
            data['attachment_path'] = path
        except Exception as e: return jsonify({"error": str(e)}), 500

    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            if full_path and os.path.exists(full_path): os.remove(full_path)
            return jsonify({"error": "Auth failed"}), 401

        new_diploma = create_diploma(db_session, data, user_id=current_user.id)
        create_log(db_session, current_user.id, f"Tambah Ijazah: {new_diploma.student_name}")
        return jsonify(new_diploma.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        if full_path and os.path.exists(full_path): os.remove(full_path)
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
    if 'collected_at' in data and data['collected_at'] in ['', 'null']:
        data['collected_at'] = None

    db_session: Session = db.SessionLocal()
    try:
        existing = get_diplomas_by_keys(db_session, {'id': data['id']})
        old_path = existing[0].attachment_path if existing else None

        # --- OPTIMIZED UPLOAD ---
        file = request.files.get('file')
        if file:
            try:
                path, _ = handle_file_upload(file, 'diplomas')
                data['attachment_path'] = path
            except Exception as e: return jsonify({"error": str(e)}), 500

        updated = update_diploma(db_session, data['id'], data)
        if not updated: return jsonify({"error": "Not found"}), 404

        if file and old_path and old_path != updated.attachment_path:
            delete_physical_file(old_path)

        current_user = get_current_user_obj(db_session)
        if current_user:
            create_log(db_session, current_user.id, f"Update Ijazah: {updated.student_name}")

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

        # --- FITUR DELETE FISIK ---
        if deleted.attachment_path:
            delete_physical_file(deleted.attachment_path)

        current_user = get_current_user_obj(db_session)
        if current_user:
            create_log(db_session, current_user.id, f"Hapus Ijazah: {deleted.student_name}")

        return jsonify(deleted.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

# (Route get_all dan get_by_keys tetap sama)
@diploma_bp.route('/get_all', methods=['GET'])
def get_all_diplomas_route():
    db_session = db.SessionLocal()
    try: return jsonify([d.to_dict() for d in get_all_diplomas(db_session)]), 200
    finally: db_session.close()

@diploma_bp.route('/get_by_keys', methods=['POST'])
def get_diplomas_by_keys_route():
    data = request.json or {}
    filters = data.get('filters', data if isinstance(data, dict) else {})
    db_session = db.SessionLocal()
    try: return jsonify([d.to_dict() for d in get_diplomas_by_keys(db_session, filters)]), 200
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: db_session.close()