from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.user import create_user, update_user, delete_user, get_all_users, get_user_by_key
from app.services.log import create_log
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/create', methods=['POST'])
@jwt_required()
def create_user_route():
    data = request.json
    required_fields = ['nuptk', 'username', 'password', 'role', 'status']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()

    try:
        new_user = create_user(db_session, data)
        
        try:
            current_user_nuptk = get_jwt_identity()
            admin_user = get_user_by_key(db_session, 'nuptk', current_user_nuptk)
            
            if admin_user:
                action = f"Pengguna  membuat user baru dengan nomor 'NUPTK': '{new_user.nuptk}'."
                create_log(db_session, admin_user[0].id, action)
            else:
                print(f"Warning Log: User dengan NUPTK {current_user_nuptk} tidak ditemukan di DB.")

        except Exception as e:

            print(f"Warning Log Error: {e}")

        return jsonify({
            "message": f"Berhasil membuat pengguna dengan nomor NUPTK: {new_user.nuptk}"
        }), 201
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"message": "Gagal: NUPTK atau Username sudah terdaftar."}), 409

    except Exception as e:
        db_session.rollback()
        print(f"Error Create User: {e}")
        return jsonify({"message": "Terjadi kesalahan internal server"}), 500
    
    finally:
        db_session.close()
    

@user_bp.route('/update', methods=['POST'])
@jwt_required()
def updated_user_route():
    data = request.json
    id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        updated_user = update_user(db_session, id, data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404
        
        try:
            current_user_nuptk = get_jwt_identity()
            admin_user = get_user_by_key(db_session, 'nuptk', current_user_nuptk)

            if not data.key():
                text = "tidak ada data"
            elif len(data.key()) == 1:
                text = f"'{data.key()[0]}'"
            else:
                text = ", ".join(f"'{k}'" for k in data.key()[:-1])
                text += f" dan '{data.key()[-1]}'"

            if admin_user:
                action = f"Pengguna  memperbarui data {text} pengguna dengan nomor 'NUPTK': '{updated_user.nuptk}'."
                create_log(db_session, admin_user[0].id, action)
            else:
                print(f"Warning Log: User dengan NUPTK {current_user_nuptk} tidak ditemukan di DB.")

        except Exception as e:
            print(f"Warning Log Error: {e}")


        return jsonify({
            "message": f"Berhasil memperbarui data pengguna dengan NUPTK: {updated_user.nuptk}"
        }), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "NUPTK already exists"}), 409

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

        return jsonify({
            "message": f"Berhasil menghapus pengguna dengan NUPTK: {deleted_user.nuptk}",
            "data": deleted_user.to_dict()
        }), 200

    finally:
        db_session.close()

@user_bp.route('/get_all', methods=['GET'])
def get_all_users_route():
    db_session: Session = db.SessionLocal()
    try:
        users = get_all_users(db_session)
        users_list = [
            user.to_dict()
        for user in users]
        return jsonify(users_list), 200

    finally:
        db_session.close()

@user_bp.route('/get_by_key', methods=['POST'])
def get_all_users_by_key_route():
    
    data = request.json

    key = data.get('key')
    value = data.get('value')
    
    if not key or not value:
        return jsonify({"error": "key and value fields are required in JSON body"}), 400

    db_session: Session = db.SessionLocal()
    try:
        users = get_user_by_key(db_session, key, value)
        
        if not users:
            return jsonify({"error": "User not found"}), 404
        
        users_list = [
            user.to_dict()
        for user in users]
        return jsonify(users_list), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
        
    finally:
        db_session.close()