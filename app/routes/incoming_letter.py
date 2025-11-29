from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.services.incoming_letter import (
    create_incoming_letter, 
    update_incoming_letter, 
    delete_incoming_letter, 
    get_all_incoming_letters, 
    get_incoming_letter_by_key
)
from app.services.user import get_user_by_key
from app.services.log import create_log
from app import db

incoming_letter_bp = Blueprint('incoming_letter', __name__)

def get_current_user_obj(db_session):
    """
    Helper function to retrieve the currently logged-in user object based on the JWT identity.
    """
    current_nuptk = get_jwt_identity()
    users = get_user_by_key(db_session, 'nuptk', current_nuptk)
    return users[0] if users else None

@incoming_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_incoming_letter_route():
    """
    Creates a new incoming letter record.

    Request Body:
        number, letter_date, received_date, sender, subject, classification_id.

    Returns:
        JSON: The created letter object or error.
    """
    data = request.json
    required_fields = ['number', 'letter_date', 'received_date', 'sender', 'subject', 'classification_id']

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
            data['received_date'] = datetime.fromisoformat(data['received_date'])
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400

        new_letter = create_incoming_letter(db_session, data, user_id=current_user.id)
        
        try:
            action = f"Pengguna '{current_user.username}' menambahkan surat masuk nomor: '{new_letter.number}'."
            create_log(db_session, current_user.id, action)
        except Exception as log_error:
            print(f"Log Error: {log_error}")

        return jsonify(new_letter.to_dict()), 201

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Nomor surat sudah terdaftar (harus unik)."}), 409
    except Exception as e:
        db_session.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        db_session.close()

@incoming_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_incoming_letter_route():
    """
    Updates an existing incoming letter.

    Request Body:
        id (int): Letter ID.
        ...other fields to update.

    Returns:
        JSON: Updated letter object.
    """
    data = request.json
    letter_id = data.get('id')
    
    if not letter_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        if 'letter_date' in data:
            data['letter_date'] = datetime.fromisoformat(data['letter_date'])
        if 'received_date' in data:
            data['received_date'] = datetime.fromisoformat(data['received_date'])

        updated_letter = update_incoming_letter(db_session, letter_id, data)
        
        if not updated_letter:
            return jsonify({"error": "Letter not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            updated_fields = list(data.keys())
            if 'id' in updated_fields: updated_fields.remove('id')
            fields_str = ", ".join(updated_fields)
            
            action = f"Pengguna '{current_user.username}' mengupdate data ({fields_str}) pada surat masuk nomor: '{updated_letter.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(updated_letter.to_dict()), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

@incoming_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_incoming_letter_route():
    """
    Deletes an incoming letter record.

    Request Body:
        id (int): Letter ID.

    Returns:
        JSON: Deleted letter data.
    """
    data = request.json
    letter_id = data.get('id')

    db_session: Session = db.SessionLocal()
    try:
        deleted_letter = delete_incoming_letter(db_session, letter_id)
        
        if not deleted_letter:
            return jsonify({"error": "Letter not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            action = f"Pengguna '{current_user.username}' menghapus surat masuk nomor: '{deleted_letter.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(deleted_letter.to_dict()), 200
    finally:
        db_session.close()

@incoming_letter_bp.route('/get_all', methods=['GET'])
def get_all_incoming_letters_route():
    """
    Retrieves all incoming letters.

    Returns:
        JSON: A list of incoming letter objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        letters = get_all_incoming_letters(db_session)
        return jsonify([l.to_dict() for l in letters]), 200
    finally:
        db_session.close()

@incoming_letter_bp.route('/get_by_key', methods=['POST'])
def get_incoming_by_key_route():
    """
    Retrieves incoming letters filtered by a specific key.

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
        letters = get_incoming_letter_by_key(db_session, key, value)
        if not letters:
            return jsonify({"message": "No letters found"}), 404
            
        return jsonify([l.to_dict() for l in letters]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()