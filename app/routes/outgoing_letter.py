from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.services.outgoing_letter import (
    create_outgoing_letter,
    update_outgoing_letter,
    delete_outgoing_letter,
    get_all_outgoing_letters,
    get_outgoing_letter_by_key
)
from app.services.user import get_user_by_key
from app.services.log import create_log
from app import db

outgoing_letter_bp = Blueprint('outgoing_letter', __name__)

def get_current_user_obj(db_session):
    """
    Helper function to retrieve the currently logged-in user object based on the JWT identity.
    """
    current_nuptk = get_jwt_identity()
    users = get_user_by_key(db_session, 'nuptk', current_nuptk)
    return users[0] if users else None

@outgoing_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_outgoing_letter_route():
    """
    Creates a new outgoing letter record.

    Request Body:
        number, letter_date, sent_date, destination, is_decree, classification_id.

    Returns:
        JSON: The created letter object or error.
    """
    data = request.json
    required_fields = ['number', 'letter_date', 'sent_date', 'destination', 'is_decree', 'classification_id']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            return jsonify({"error": "User authentication failed"}), 401

        try:
            data['letter_date'] = datetime.fromisoformat(data['letter_date'])
            data['sent_date'] = datetime.fromisoformat(data['sent_date'])
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        new_letter = create_outgoing_letter(db_session, data, user_id=current_user.id)
        
        try:
            action = f"Pengguna '{current_user.username}' menambahkan surat keluar nomor: '{new_letter.number}'."
            create_log(db_session, current_user.id, action)
        except Exception:
            pass

        return jsonify(new_letter.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_outgoing_letter_route():
    """
    Updates an existing outgoing letter.

    Request Body:
        id (int): Letter ID.
        ...other fields to update.

    Returns:
        JSON: Updated letter object.
    """
    data = request.json
    letter_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        if 'letter_date' in data:
            data['letter_date'] = datetime.fromisoformat(data['letter_date'])
        if 'sent_date' in data:
            data['sent_date'] = datetime.fromisoformat(data['sent_date'])

        updated_letter = update_outgoing_letter(db_session, letter_id, data)
        
        if not updated_letter:
            return jsonify({"error": "Letter not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            updated_fields = list(data.keys())
            if 'id' in updated_fields: updated_fields.remove('id')
            fields_str = ", ".join(updated_fields)
            action = f"Pengguna '{current_user.username}' mengupdate ({fields_str}) surat keluar nomor: '{updated_letter.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(updated_letter.to_dict()), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

@outgoing_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_outgoing_letter_route():
    """
    Deletes an outgoing letter record.

    Request Body:
        id (int): Letter ID.

    Returns:
        JSON: Deleted letter data.
    """
    data = request.json
    letter_id = data.get('id')

    db_session: Session = db.SessionLocal()
    try:
        deleted_letter = delete_outgoing_letter(db_session, letter_id)
        
        if not deleted_letter:
            return jsonify({"error": "Letter not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            action = f"Pengguna '{current_user.username}' menghapus surat keluar nomor: '{deleted_letter.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(deleted_letter.to_dict()), 200
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_all', methods=['GET'])
def get_all_outgoing_letters_route():
    """
    Retrieves all outgoing letters.

    Returns:
        JSON: A list of outgoing letter objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        letters = get_all_outgoing_letters(db_session)
        return jsonify([l.to_dict() for l in letters]), 200
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_by_key', methods=['POST'])
def get_outgoing_by_key_route():
    """
    Retrieves outgoing letters filtered by a specific key.

    Request Body:
        key (str): Column name.
        value (str): Search value.

    Returns:
        JSON: A list of matching letter objects.
    """
    data = request.json
    key = data.get('key')
    value = data.get('value')

    if not key or not value:
        return jsonify({"error": "Key and value are required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        letters = get_outgoing_letter_by_key(db_session, key, value)
        return jsonify([l.to_dict() for l in letters]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()