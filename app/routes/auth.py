from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.models.user import user
from app.services.auth import login_user
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    nuptk = data.get('nuptk')
    kata_sandi = data.get('password')

    if not nuptk or not kata_sandi:
        return jsonify({"error": "NUPTK and password are required"}), 400

    db_session: Session = db.SessionLocal()
    existing_user = login_user(db_session, nuptk, kata_sandi)
    db_session.close()

    if not user:
        return jsonify({"error": "Invalid NUPTK or password"}), 401

    return jsonify({
        "nuptk": existing_user.nuptk,
        "username": existing_user.username,
    }), 200