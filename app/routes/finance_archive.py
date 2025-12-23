import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

# Import Services
from app.models.finance_archive import FinanceArchive
from app.services.finance_archive import (
    create_finance_archive, update_finance_archive, 
    delete_finance_archive, get_all_finance_archives,
    get_finance_archives_paginated
)
from app.services.teacher import get_teachers_by_keys
from app.services.log import create_log
from app import db
from app.utils.file_helper import handle_file_upload, delete_physical_file

finance_bp = Blueprint('finance_archive', __name__)

def get_current_actor_id(db_session):
    """Helper: Get Teacher ID from JWT Identity (NIP) for logging"""
    try:
        current_identity = get_jwt_identity()
        teachers = get_teachers_by_keys(db_session, {'identity_number': current_identity})
        return teachers[0].id if teachers else None
    except:
        return None

@finance_bp.route('/create', methods=['POST'])
@jwt_required()
def create_route():
    data = request.form.to_dict()
    if not data.get('title') or not data.get('fiscal_year'):
        return jsonify({"error": "Judul dan Tahun Anggaran wajib diisi"}), 400
            
    # Handle File Upload
    file = request.files.get('file')
    attachment_path = None
    if file:
        try:
            attachment_path, _ = handle_file_upload(file, 'finance_archives')
            data['attachment_path'] = attachment_path
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    db_session = db.SessionLocal()
    try:
        # [UBAH] Create tanpa user_id
        new_data = create_finance_archive(db_session, data)
        
        # Logging Action
        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Menambahkan Arsip Keuangan: '{new_data.title}'")
        
        return jsonify(new_data.to_dict()), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@finance_bp.route('/update', methods=['POST'])
@jwt_required()
def update_route():
    data = request.form.to_dict()
    archive_id = data.get('id')
    if not archive_id: return jsonify({"error": "ID required"}), 400

    db_session = db.SessionLocal()
    try:
        # Cek data lama & file
        curr = db_session.query(FinanceArchive).filter(FinanceArchive.id == archive_id).first()
        if not curr: return jsonify({"error": "Data not found"}), 404
        old_path = curr.attachment_path

        file = request.files.get('file')
        if file:
            try:
                path, _ = handle_file_upload(file, 'finance_archives')
                data['attachment_path'] = path
            except Exception as e: return jsonify({"error": str(e)}), 500

        updated = update_finance_archive(db_session, archive_id, data)
        
        # Hapus file lama
        if file and old_path and old_path != updated.attachment_path:
            delete_physical_file(old_path)

        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Update Arsip Keuangan: '{updated.title}'")

        return jsonify(updated.to_dict()), 200
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@finance_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_route():
    data = request.json or {}
    archive_id = data.get('id')
    
    db_session = db.SessionLocal()
    try:
        deleted = delete_finance_archive(db_session, archive_id)
        if not deleted: return jsonify({"error": "Not found"}), 404

        if deleted.attachment_path:
             delete_physical_file(deleted.attachment_path)
        
        actor_id = get_current_actor_id(db_session)
        if actor_id:
            create_log(db_session, actor_id, f"Hapus Arsip Keuangan: '{deleted.title}'")

        return jsonify({"status": "deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@finance_bp.route('/get_all', methods=['GET'])
def get_all_route():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({"error": "Invalid page or per_page parameters"}), 400
    except ValueError:
        return jsonify({"error": "Page and per_page must be integers"}), 400
    
    db_session = db.SessionLocal()
    try:
        result = get_finance_archives_paginated(db_session, page=page, per_page=per_page)
        return jsonify({
            'finance_archives': [x.to_dict() for x in result['finance_archives']],
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages']
            }
        }), 200
    finally:
        db_session.close()