from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import Session
from app.services.auth import login_user
from app.services.log import create_log
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticates a user and provides a JWT access token.

    Request Body:
        nuptk (str): The user's unique identification number.
        password (str): The user's password.

    Returns:
        JSON: Access token and welcome message if successful, error message otherwise.
    """
    data = request.json
    nuptk = data.get('nuptk')
    password = data.get('password')

    if not nuptk or not password:
        return jsonify({"message": "NUPTK dan password wajib diisi"}), 400

    db_session: Session = db.SessionLocal()
    
    try:
        existing_user = login_user(db_session, nuptk, password)

        if not existing_user:
            return jsonify({"message": "NUPTK atau kata sandi tidak valid"}), 401

        access_token = create_access_token(identity=str(existing_user.nuptk))
        username = existing_user.username 
        
        try:
            action = f"Pengguna melakukan login."
            create_log(db_session, existing_user.id, action)
        except Exception as e:
            print(f"Login Log Error: {e}") 

        return jsonify({
            "message": f"Selamat Datang! {username}!",
            "access_token": access_token
        }), 200

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"message": "Terjadi kesalahan pada server"}), 500
        
    finally:
        db_session.close()