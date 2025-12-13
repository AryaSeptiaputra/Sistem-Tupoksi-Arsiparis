from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.teacher import create_teacher, update_teacher, delete_teacher, get_all_teachers, get_teachers_by_keys
from app.services.log import create_log
from app import db

# Inisialisasi Blueprint
teacher_bp = Blueprint('teacher', __name__)

@teacher_bp.route('/create', methods=['POST'])
@jwt_required()
def create_teacher_route():
    """
    Creates a new teacher profile.
    JSON Payload: identity_number, full_name, gender, employment_status, status, rank (opt), address (opt)
    """
    data = request.json
    required_fields = ['identity_number', 'full_name', 'gender', 'employment_status', 'status']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()

    try:
        new_teacher = create_teacher(db_session, data)
        
        # --- Logging Logic ---
        try:
            current_identity = get_jwt_identity()
            # Cari ID aktor (Teacher) berdasarkan identity_number yang login
            actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            if actor:
                action = f"Menambahkan Guru/Pegawai baru: '{new_teacher.full_name}' ({new_teacher.identity_number})."
                create_log(db_session, actor[0].id, action)
        except Exception as e:
            print(f"Warning Log Error: {e}")
        # ---------------------

        return jsonify({
            "message": f"Berhasil menambahkan data guru: {new_teacher.full_name}"
        }), 201
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"message": "NIP/NUPTK sudah terdaftar."}), 409
    except Exception as e:
        db_session.rollback()
        print(f"Error Create Teacher: {e}")
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        db_session.close()

@teacher_bp.route('/update', methods=['POST'])
@jwt_required()
def update_teacher_route():
    data = request.json
    teacher_id = data.get('id')
    
    if not teacher_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated = update_teacher(db_session, teacher_id, data)
        if not updated:
            return jsonify({"error": "Teacher not found"}), 404
        
        # --- Logging ---
        try:
            current_identity = get_jwt_identity()
            actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            if actor:
                create_log(db_session, actor[0].id, f"Memperbarui data guru: {updated.full_name}")
        except Exception:
            pass
        # ---------------

        return jsonify({"message": "Data berhasil diperbarui"}), 200

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "NIP/NUPTK conflict"}), 409
    finally:
        db_session.close()

@teacher_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_teacher_route():
    data = request.json
    teacher_id = data.get('id')
    
    if not teacher_id:
        return jsonify({"error": "id is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_teacher(db_session, teacher_id)
        if not deleted:
            return jsonify({"error": "Teacher not found"}), 404
        
        # --- Logging ---
        try:
            current_identity = get_jwt_identity()
            actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            if actor:
                create_log(db_session, actor[0].id, f"Menghapus data guru: {deleted.full_name}")
        except Exception:
            pass
        # ---------------

        return jsonify({"message": "Data berhasil dihapus"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@teacher_bp.route('/get_all', methods=['GET'])
def get_all_teachers_route():
    db_session: Session = db.SessionLocal()
    try:
        teachers = get_all_teachers(db_session)
        return jsonify([t.to_dict() for t in teachers]), 200
    finally:
        db_session.close()

@teacher_bp.route('/get_by_keys', methods=['POST'])
def get_teachers_by_keys_route():
    data = request.json
    filters = data.get('filters')
    
    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        teachers = get_teachers_by_keys(db_session, filters)
        return jsonify([t.to_dict() for t in teachers]), 200
    finally:
        db_session.close()