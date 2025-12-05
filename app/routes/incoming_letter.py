import os

from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.incoming_letter import create_incoming_letter, update_incoming_letter, delete_incoming_letter, get_all_incoming_letters, get_incoming_letters_by_keys
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db

incoming_letter_bp = Blueprint('incoming_letter', __name__)

def get_current_user_obj(db_session: Session):
    """Helper function to retrieve the currently logged-in user object.

    Uses the JWT identity (NUPTK) from the request context to fetch
    the full User object from the database using the plural service with a filter.

    Args:
        db_session (Session): The active database session.

    Returns:
        User | None: The User object if found, otherwise None.
    """
    current_nuptk = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_nuptk})
    return users[0] if users else None

@incoming_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_incoming_letter_route():
    """Creates a new incoming letter record with file attachment.

    Requires a valid JWT access token. Accepts multipart/form-data to handle
    text fields and an optional file upload. The file is saved to the local
    storage system.

    Args:
        No explicit arguments. Expects Multipart/Form-Data payload:
        number (str): The official letter number (must be unique).
        letter_date (str): Date on the letter (YYYY-MM-DD).
        received_date (str): Date received (YYYY-MM-DD).
        sender (str): The sender of the letter.
        subject (str): The subject or title of the letter.
        classification_id (int): Foreign key linking to a classification.
        file (FileStorage, optional): The document file to upload.

    Returns:
        tuple[Response, int]:
            * 201: JSON of the created letter including attachment path.
            * 400: Missing required fields.
            * 401: User authentication failed.
            * 409: Letter number already exists.
            * 500: Internal Server Error or File Save Error.
    """

    data = request.form.to_dict()
    required_fields = ['number', 'letter_date', 'received_date', 'sender', 'subject', 'classification_id']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage', 'documents', 'incoming_letters')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file = request.files.get('file')
    full_path = None
    
    if file:
        try:
            filename = secure_filename(file.filename)
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(full_path)
            
            data['attachment_path'] = os.path.join('storage', 'documents', 'incoming_letters', filename)
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    
    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            if full_path and os.path.exists(full_path):
                os.remove(full_path)
            return jsonify({"error": "User authentication failed"}), 401
        
        new_letter = create_incoming_letter(db_session, data, user_id=current_user.id)
        
        try:
            action = f"Pengguna '{current_user.username}' menambahkan surat masuk nomor: '{new_letter.number}'."
            create_log(db_session, current_user.id, action)
        except Exception as log_error:
            print(f"Log Error: {log_error}")

        return jsonify(new_letter.to_dict()), 201

    except IntegrityError:
        db_session.rollback()
        if full_path and os.path.exists(full_path):
            os.remove(full_path)
        return jsonify({"error": "Nomor surat sudah terdaftar (harus unik)."}), 409
    except Exception as e:
        db_session.rollback()
        if full_path and os.path.exists(full_path):
            os.remove(full_path)
        print(f"Error Incoming Letter: {e}") 
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        db_session.close()

@incoming_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_incoming_letter_route():
    """Updates an existing incoming letter.

    Requires a valid JWT access token. Updates specified fields and logs
    the activity.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the letter to update (Required).
        ... (Any other field from create_incoming_letter_route to update).

    Returns:
        tuple[Response, int]:
            * 200: JSON of the updated letter.
            * 400: Missing 'id'.
            * 404: Letter not found.
    """
    try:
        # 1. Coba baca data (Support JSON atau Form Data)
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()
        
        letter_id = data.get('id')
        if not letter_id:
            return jsonify({"error": "ID surat wajib ada"}), 400

        # 2. Konversi Tipe Data (Penting!)
        # Karena FormData mengirim angka sebagai string, kita harus ubah manual
        try:
            if 'classification_id' in data and data['classification_id']:
                data['classification_id'] = int(data['classification_id'])
        except ValueError:
             return jsonify({"error": "Classification ID harus berupa angka"}), 400

        # 3. Handle File Upload (Jika user mengganti file saat edit)
        file = request.files.get('file')
        if file:
            try:
                UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage', 'documents', 'incoming_letters')
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                filename = secure_filename(file.filename)
                full_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(full_path)
                
                # Masukkan path baru ke data untuk diupdate di DB
                data['attachment_path'] = os.path.join('storage', 'documents', 'incoming_letters', filename)
            except Exception as e:
                return jsonify({"error": f"Gagal upload file baru: {str(e)}"}), 500

        # 4. Proses Update ke Database
        db_session: Session = db.SessionLocal()
        try:
            updated_letter = update_incoming_letter(db_session, letter_id, data)
            
            if not updated_letter:
                return jsonify({"error": "Surat tidak ditemukan"}), 404

            # Log Aktivitas
            current_user = get_current_user_obj(db_session)
            if current_user:
                # Filter field yang diupdate untuk log
                updated_fields = [k for k in data.keys() if k not in ['id', 'user_id']]
                fields_str = ", ".join(updated_fields)
                
                action = f"Pengguna '{current_user.username}' mengupdate data ({fields_str}) pada surat masuk: '{updated_letter.number}'."
                create_log(db_session, current_user.id, action)

            return jsonify(updated_letter.to_dict()), 200

        except IntegrityError:
            db_session.rollback()
            return jsonify({"error": "Nomor surat bentrok dengan data lain."}), 409
        except Exception as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            db_session.close()

    except Exception as e:
        print(f"SYSTEM ERROR: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@incoming_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_incoming_letter_route():
    """Deletes an incoming letter record.

    Requires a valid JWT access token. Removes the record and logs the
    deletion activity.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the letter to delete.

    Returns:
        tuple[Response, int]:
            * 200: JSON data of the deleted letter.
            * 404: Letter not found.
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
    """Retrieves all incoming letters.

    Fetches a list of all incoming letters currently stored in the database.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list of incoming letter objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        letters = get_all_incoming_letters(db_session)
        return jsonify([l.to_dict() for l in letters]), 200
    finally:
        db_session.close()

@incoming_letter_bp.route('/get_by_keys', methods=['POST'])
def get_incoming_by_keys_route():
    """Retrieves incoming letters filtered by multiple keys.

    Allows advanced filtering using a dictionary of parameters.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): Dictionary of filter criteria.
            Example: {"sender": "Dinas", "classification_id": 1}

    Returns:
        tuple[Response, int]:
            * 200: A list of letters matching the filters.
            * 400: Missing 'filters' dictionary or invalid format.
    """
    data = request.json
    filters = data.get('filters')

    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        letters = get_incoming_letters_by_keys(db_session, filters)
        return jsonify([l.to_dict() for l in letters]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()