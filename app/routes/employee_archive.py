import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

# Import Models & Services
from app.models.employee_archive import EmployeeArchive
from app.models.teacher import Teacher
from app.services.employee_archive import (
    create_employee_archive, update_employee_archive, 
    delete_employee_archive, get_all_employee_archives
)
from app.services.teacher import get_teachers_by_keys # Untuk Log Actor
from app.services.log import create_log
from app import db
from app.utils.file_helper import handle_file_upload, delete_physical_file

employee_archive_bp = Blueprint('employee_archive', __name__)

def get_current_actor_id(db_session):
    """Helper: Get Teacher ID of current user for logging"""
    try:
        identity = get_jwt_identity()
        teachers = get_teachers_by_keys(db_session, {'identity_number': identity})
        return teachers[0].id if teachers else None
    except:
        return None

@employee_archive_bp.route('/create', methods=['POST'])
@jwt_required()
def create_route():
    data = request.form.to_dict()
    
    if not data.get('document_name') or not data.get('owner_id'):
        return jsonify({"error": "Nama Dokumen dan Pemilik wajib diisi"}), 400
        
    # Validasi file
    file = request.files.get('file')
    if file:
        try:
            path, _ = handle_file_upload(file, 'employee_archives')
            data['attachment_path'] = path
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    db_session = db.SessionLocal()
    try:
        new_data = create_employee_archive(db_session, data)
        
        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Upload Arsip Pegawai: {new_data.document_name}")
        
        return jsonify(new_data.to_dict()), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@employee_archive_bp.route('/update', methods=['POST'])
@jwt_required()
def update_route():
    data = request.form.to_dict()
    if not data.get('id'): return jsonify({"error": "ID required"}), 400

    db_session = db.SessionLocal()
    try:
        curr = db_session.query(EmployeeArchive).filter(EmployeeArchive.id == data.get('id')).first()
        if not curr: return jsonify({"error": "Not found"}), 404
        old_path = curr.attachment_path

        file = request.files.get('file')
        if file:
            try:
                path, _ = handle_file_upload(file, 'employee_archives')
                data['attachment_path'] = path
            except Exception as e: return jsonify({"error": str(e)}), 500

        updated = update_employee_archive(db_session, data.get('id'), data)
        
        if file and old_path and old_path != updated.attachment_path:
            delete_physical_file(old_path)
        
        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Update Arsip Pegawai: {updated.document_name}")

        return jsonify(updated.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@employee_archive_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_route():
    data = request.json or {}
    db_session = db.SessionLocal()
    try:
        deleted = delete_employee_archive(db_session, data.get('id'))
        if deleted:
            if deleted.attachment_path: delete_physical_file(deleted.attachment_path)
            actor_id = get_current_actor_id(db_session)
            if actor_id: create_log(db_session, actor_id, f"Hapus Arsip Pegawai: {deleted.document_name}")
            return jsonify({"status": "deleted"}), 200
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@employee_archive_bp.route('/get_all', methods=['GET'])
def get_all_route():
    db_session = db.SessionLocal()
    try: return jsonify([x.to_dict() for x in get_all_employee_archives(db_session)]), 200
    finally: db_session.close()