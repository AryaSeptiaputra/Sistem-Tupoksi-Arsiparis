import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.user import get_user, update_profile, change_password
from app.services.log import create_log
from app.utils.current_user import get_current_user_id
from app import db

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__)

@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me_route():
    db_session: Session = db.SessionLocal()
    try:
        user = get_user(db_session, get_current_user_id())
        if not user:
            return jsonify({"error": "Akun tidak ditemukan"}), 404
        return jsonify(user.to_dict()), 200
    finally:
        db_session.close()

@user_bp.route('/update', methods=['POST'])
@jwt_required()
def update_me_route():
    """
    Payload: username, display_name
    """
    data = request.json or {}
    db_session: Session = db.SessionLocal()
    try:
        user_id = get_current_user_id()
        updated_user = update_profile(db_session, user_id, data.get('username'), data.get('display_name'))
        if not updated_user:
            return jsonify({"error": "Akun tidak ditemukan"}), 404

        create_log(db_session, user_id, "Memperbarui informasi akun.")
        return jsonify({"message": "Informasi akun berhasil diperbarui", "data": updated_user.to_dict()}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Username sudah dipakai."}), 409
    finally:
        db_session.close()

@user_bp.route('/change_password', methods=['POST'])
@jwt_required()
def change_password_route():
    """
    Payload: old_password, new_password
    """
    data = request.json or {}
    db_session: Session = db.SessionLocal()
    try:
        user_id = get_current_user_id()
        updated_user = change_password(db_session, user_id, data.get('old_password'), data.get('new_password') or '')
        if not updated_user:
            return jsonify({"error": "Akun tidak ditemukan"}), 404

        create_log(db_session, user_id, "Mengganti kata sandi akun.")
        return jsonify({"message": "Kata sandi berhasil diganti"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()
