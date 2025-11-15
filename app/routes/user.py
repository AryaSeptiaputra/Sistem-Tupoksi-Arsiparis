from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import user
from app.services.user import create_user, update_user, delete_user, get_all_users, get_user_by_key
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/create', methods=['POST'])
def create_user_route():
    data = request.json

    required_fields = ['nuptk', 'username', 'password', 'role', 'status']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        new_user = create_user(db_session, data)
        return jsonify({
        new_user.to_dict()
    }), 201

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "NUPTK already exists"}), 409
    
    finally:
        db_session.close()
    

@user_bp.route('/update', methods=['POST'])
def updated_user_route():
    data = request.json
    nuptk = data.get('nuptk')
    
    db_session: Session = db.SessionLocal()
    try:
        updated_user = update_user(db_session, nuptk, data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            update_user.to_dict()
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
def delete_user_route():
    data = request.json
    nuptk = data.get('nuptk')
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_user = delete_user(db_session, nuptk)
        if not deleted_user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            delete_user.to_dict()
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