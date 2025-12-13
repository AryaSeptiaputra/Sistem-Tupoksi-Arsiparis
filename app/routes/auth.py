from flask import Blueprint, request, jsonify, session
from sqlalchemy.orm import Session
from flask_jwt_extended import create_access_token
from app.services.auth import login_user
from app.services.log import create_log
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # Frontend mengirim key 'nuptk', tapi di backend kita anggap sebagai 'identity_number'
    identity_input = data.get('nuptk') 
    password = data.get('password')

    if not identity_input or not password:
        return jsonify({"message": "NIP/NUPTK dan password wajib diisi"}), 400

    db_session: Session = db.SessionLocal()
    
    try:
        # Panggil Service Login
        existing_user = login_user(db_session, identity_input, password)

        if not existing_user:
            return jsonify({"message": "NIP/NUPTK atau kata sandi salah"}), 401

        # Pastikan data guru tersedia (safety check)
        if not existing_user.teacher:
             return jsonify({"message": "Akun User ditemukan tapi data Guru korup/hilang."}), 500

        user_role = str(existing_user.role)

        # ==================================================================
        # 🔥 FLASK SESSION (SERVER SIDE)
        # ==================================================================
        session.permanent = True
        session['user_id'] = existing_user.id
        session['role'] = user_role
        # Gunakan Nama Lengkap Guru sebagai display name
        session['username'] = existing_user.teacher.full_name 
        # ==================================================================

        # --- JWT Claims ---
        additional_claims = {
            "id": existing_user.id,
            "identity_number": existing_user.teacher.identity_number, # Pengganti NUPTK lama
            "full_name": existing_user.teacher.full_name,             # Pengganti Username lama
            "role": user_role,
            "status": str(existing_user.status),
            "created_at": existing_user.created_at.strftime("%Y-%m-%d")
        }

        # Identity token menggunakan Identity Number (NIP/NUPTK)
        access_token = create_access_token(
            identity=str(existing_user.teacher.identity_number),
            additional_claims=additional_claims
        )

        # --- LOG AKTIVITAS ---
        try:
            action = f"Pengguna '{existing_user.teacher.full_name}' melakukan login."
            create_log(db_session, existing_user.teacher.id, action)
        except Exception as e:
            print(f"Login Log Error: {e}") 

        return jsonify({
            "message": f"Selamat Datang, {existing_user.teacher.full_name}!",
            "access_token": access_token
        }), 200

    except Exception as e:
        print(f"Login Error: {e}")
        return jsonify({"message": "Terjadi kesalahan pada server"}), 500
        
    finally:
        db_session.close()