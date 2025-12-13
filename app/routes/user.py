from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.user import create_user, update_user, delete_user, get_all_users, get_users_by_keys
from app.services.teacher import get_teachers_by_keys
from app.services.log import create_log
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/create', methods=['POST'])
@jwt_required()
def create_user_route():
    """
    Payload: teacher_id, password, role, status
    """
    data = request.json
    required_fields = ['teacher_id', 'password', 'role', 'status']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()

    try:
        new_user = create_user(db_session, data)
        
        # --- Logging ---
        try:
            # Ambil identitas admin yang sedang login
            current_identity = get_jwt_identity() 
            # Cari data Teacher milik admin tersebut
            admin_actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            
            if admin_actor:
                target_teacher = new_user.teacher.full_name if new_user.teacher else "Unknown"
                action = f"Membuat akun pengguna untuk guru: '{target_teacher}'."
                create_log(db_session, admin_actor[0].id, action)
        except Exception as e:
            print(f"Log Error: {e}")
        # ---------------

        return jsonify({
            "message": "Akun pengguna berhasil dibuat."
        }), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db_session.rollback()
        return jsonify({"message": "Database Error: Kemungkinan duplikasi data."}), 409
    except Exception as e:
        db_session.rollback()
        print(f"Error Create User: {e}")
        return jsonify({"message": "Internal Server Error"}), 500
    finally:
        db_session.close()

@user_bp.route('/update', methods=['POST'])
@jwt_required()
def updated_user_route():
    data = request.json
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated_user = update_user(db_session, user_id, data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404
        
        # --- Logging ---
        try:
            current_identity = get_jwt_identity()
            admin_actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            
            if admin_actor:
                target_name = updated_user.teacher.full_name if updated_user.teacher else "Unknown"
                action = f"Memperbarui akun pengguna: '{target_name}'."
                create_log(db_session, admin_actor[0].id, action)
        except Exception:
            pass
        # ---------------

        return jsonify({"message": "Data pengguna berhasil diperbarui"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

@user_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_user_route():
    data = request.json
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({"error": "id is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_user = delete_user(db_session, user_id)
        if not deleted_user:
            return jsonify({"error": "User not found"}), 404
        
        # --- Logging ---
        try:
            current_identity = get_jwt_identity()
            admin_actor = get_teachers_by_keys(db_session, {'identity_number': current_identity})
            if admin_actor:
                target_name = deleted_user.teacher.full_name if deleted_user.teacher else "Unknown"
                create_log(db_session, admin_actor[0].id, f"Menghapus akun pengguna: {target_name}")
        except Exception:
            pass
        # ---------------

        return jsonify({"message": "Akun berhasil dihapus"}), 200

    finally:
        db_session.close()

@user_bp.route('/get_all', methods=['GET'])
def get_all_users_route():
    db_session: Session = db.SessionLocal()
    try:
        users = get_all_users(db_session)
        return jsonify([user.to_dict() for user in users]), 200
    finally:
        db_session.close()

@user_bp.route('/get_by_keys', methods=['POST'])
def get_users_by_keys_route():
    data = request.json
    filters = data.get('filters')
    
    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        users = get_users_by_keys(db_session, filters)
        return jsonify([user.to_dict() for user in users]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()