from flask import Blueprint, request, jsonify, session
from flask.typing import ResponseReturnValue
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from flask_jwt_extended import create_access_token
from app.services.auth import login_user
from app.services.user import record_login
from app.services.log import create_log
from app import db
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login() -> ResponseReturnValue:
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username dan password wajib diisi"}), 400

    db_session: Session = db.SessionLocal()

    try:
        existing_user = login_user(db_session, username, password)

        if not existing_user:
            return jsonify({"message": "Username atau kata sandi salah"}), 401

        record_login(db_session, existing_user)

        session.permanent = True
        session['user_id'] = existing_user.id
        session['username'] = existing_user.display_name

        additional_claims = {
            "id": existing_user.id,
            "username": existing_user.username,
            "display_name": existing_user.display_name,
            # Format tanggal: 2026-10-18
            "created_at": existing_user.created_at.strftime("%Y-%m-%d"),
        }

        access_token = create_access_token(
            identity=str(existing_user.id),
            additional_claims=additional_claims
        )

        try:
            create_log(db_session, existing_user.id, f"Pengguna '{existing_user.display_name}' melakukan login.")
        except SQLAlchemyError:
            logger.error("Gagal mencatat log login", exc_info=True)

        return jsonify({
            "message": f"Selamat Datang, {existing_user.display_name}!",
            "access_token": access_token
        }), 200

    except Exception:
        logger.error("Login gagal", exc_info=True)
        return jsonify({"message": "Terjadi kesalahan pada server"}), 500

    finally:
        db_session.close()
