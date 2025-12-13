from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.classification import (
    create_classification, update_classification, delete_classification, 
    get_all_classifications, get_classifications_by_keys
)
from app.services.log import create_log
from app.services.teacher import get_teachers_by_keys # Untuk logging actor
from app import db

classification_bp = Blueprint('classification', __name__)

@classification_bp.route('/create', methods=['POST'])
@jwt_required()
def create_classification_route():
    data = request.json
    if not data.get('name') or not data.get('code'):
        return jsonify({"error": "Name and Code are required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        new_cls = create_classification(db_session, data)
        
        # Logging
        try:
            current_identity = get_jwt_identity()
            actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            if actor:
                create_log(db_session, actor[0].id, f"Menambah Klasifikasi: {new_cls.code} - {new_cls.name}")
        except Exception: pass

        return jsonify(new_cls.to_dict()), 201

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Kode atau Nama Klasifikasi sudah ada."}), 409
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@classification_bp.route('/update', methods=['POST'])
@jwt_required()
def update_classification_route():
    data = request.json
    if not data.get('id'):
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated = update_classification(db_session, data['id'], data)
        if not updated:
            return jsonify({"error": "Not found"}), 404
            
        return jsonify(updated.to_dict()), 200

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Duplicate Name/Code"}), 409
    finally:
        db_session.close()

@classification_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_classification_route():
    data = request.json
    if not data.get('id'):
        return jsonify({"error": "ID required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_classification(db_session, data['id'])
        if not deleted:
            return jsonify({"error": "Not found"}), 404
        
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        # Menangani error jika klasifikasi sedang dipakai oleh surat (Constraint Error)
        return jsonify({"error": "Gagal hapus: Klasifikasi ini sedang digunakan oleh arsip surat."}), 400
    finally:
        db_session.close()

@classification_bp.route('/get_all', methods=['GET'])
def get_all_route():
    db_session: Session = db.SessionLocal()
    try:
        results = get_all_classifications(db_session)
        return jsonify([r.to_dict() for r in results]), 200
    finally:
        db_session.close()

@classification_bp.route('/get_by_keys', methods=['POST'])
def get_by_keys_route():
    data = request.json
    filters = data.get('filters')
    if not filters: return jsonify({"error": "Filters required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        results = get_classifications_by_keys(db_session, filters)
        return jsonify([r.to_dict() for r in results]), 200
    finally:
        db_session.close()