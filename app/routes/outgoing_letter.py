import os

from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.outgoing_letter import create_outgoing_letter, update_outgoing_letter, delete_outgoing_letter, get_all_outgoing_letters, get_outgoing_letters_by_keys
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db

outgoing_letter_bp = Blueprint('outgoing_letter', __name__)

@outgoing_letter_bp.route('/view', methods=['GET'])
def diploma_page():
    """
    Menampilkan halaman manajemen Ijazah (Frontend).
    URL: http://localhost:5000/diploma/view
    """

    return render_template('outgoing_letter.html')

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

@outgoing_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_outgoing_letter_route():
    """Creates a new outgoing letter record with file attachment.

    Requires a valid JWT access token. Accepts multipart/form-data to handle
    text fields and an optional file upload. The file is saved to the local
    storage system.

    Args:
        No explicit arguments. Expects Multipart/Form-Data payload:
        number (str): The official letter number (must be unique).
        letter_date (str): Date on the letter (YYYY-MM-DD).
        sent_date (str): Date the letter was sent (YYYY-MM-DD).
        destination (str): The recipient or destination of the letter.
        is_decree (str|bool): 'true' if the letter is a decree, else 'false'.
        classification_id (int): Foreign key linking to a classification.
        file (FileStorage, optional): The document file to upload.

    Returns:
        tuple[Response, int]:
            * 201: JSON of the created letter including attachment path.
            * 400: Missing required fields.
            * 401: User authentication failed.
            * 500: Internal Server Error or File Save Error.
    """
    data = request.form.to_dict()
    
    if 'is_decree' in data:
        if isinstance(data['is_decree'], str):
            data['is_decree'] = data['is_decree'].lower() == 'true'

    required_fields = ['number', 'letter_date', 'sent_date', 'destination', 'is_decree', 'classification_id']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage', 'documents', 'outgoing_letters')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file = request.files.get('file')
    full_path = None 
    
    if file:
        try:
            filename = secure_filename(file.filename)
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(full_path)
            
            data['attachment_path'] = os.path.join('storage', 'documents', 'outgoing_letters', filename)
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            if full_path and os.path.exists(full_path):
                os.remove(full_path)
            return jsonify({"error": "User authentication failed"}), 401

        new_letter = create_outgoing_letter(db_session, data, user_id=current_user.id)
        
        try:
            action = f"Pengguna '{current_user.username}' menambahkan surat keluar nomor: '{new_letter.number}'."
            create_log(db_session, current_user.id, action)
        except Exception:
            pass

        return jsonify(new_letter.to_dict()), 201

    except Exception as e:
        db_session.rollback()
        if full_path and os.path.exists(full_path):
            os.remove(full_path)
            
        print(f"Error Outgoing Letter: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        db_session.close()

@outgoing_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_outgoing_letter_route():
    """Updates an existing outgoing letter.

    Requires a valid JWT access token. Updates specific fields provided in
    the payload and logs the update activity.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the letter to update (Required).
        ... (Any other field from create_outgoing_letter_route to update).

    Returns:
        tuple[Response, int]:
            * 200: JSON of the updated letter.
            * 400: Missing 'id'.
            * 404: Letter not found.
    """
    import os

from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.outgoing_letter import create_outgoing_letter, update_outgoing_letter, delete_outgoing_letter, get_all_outgoing_letters, get_outgoing_letters_by_keys
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db

outgoing_letter_bp = Blueprint('outgoing_letter', __name__)

@outgoing_letter_bp.route('/view', methods=['GET'])
def diploma_page():
    """Menampilkan halaman manajemen Surat Keluar (Frontend)."""
    return render_template('outgoing_letter.html')

def get_current_user_obj(db_session: Session):
    current_nuptk = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_nuptk})
    return users[0] if users else None

@outgoing_letter_bp.route('/create', methods=['POST'])
@jwt_required()
def create_outgoing_letter_route():
    try:
        data = request.form.to_dict()
        
        # --- KONVERSI DATA ---
        if 'is_decree' in data:
            if isinstance(data['is_decree'], str):
                data['is_decree'] = data['is_decree'].lower() == 'true'
        
        # Konversi Classification ID ke Int
        try:
            if 'classification_id' in data:
                data['classification_id'] = int(data['classification_id'])
        except ValueError:
             return jsonify({"error": "Classification ID harus angka"}), 400
        # ---------------------

        required_fields = ['number', 'letter_date', 'sent_date', 'destination', 'classification_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400
        
        UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage', 'documents', 'outgoing_letters')
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file = request.files.get('file')
        full_path = None 
        
        if file:
            try:
                filename = secure_filename(file.filename)
                full_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(full_path)
                data['attachment_path'] = os.path.join('storage', 'documents', 'outgoing_letters', filename)
            except Exception as e:
                return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

        db_session: Session = db.SessionLocal()
        try:
            current_user = get_current_user_obj(db_session)
            if not current_user:
                if full_path and os.path.exists(full_path):
                    os.remove(full_path)
                return jsonify({"error": "User authentication failed"}), 401

            new_letter = create_outgoing_letter(db_session, data, user_id=current_user.id)
            
            try:
                action = f"Pengguna '{current_user.username}' menambahkan surat keluar nomor: '{new_letter.number}'."
                create_log(db_session, current_user.id, action)
            except Exception:
                pass

            return jsonify(new_letter.to_dict()), 201

        except Exception as e:
            db_session.rollback()
            if full_path and os.path.exists(full_path):
                os.remove(full_path)
            print(f"Error Create Outgoing: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            db_session.close()

    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500


@outgoing_letter_bp.route('/update', methods=['POST'])
@jwt_required()
def update_outgoing_letter_route():
    try:
        # 1. BACA DATA (Support Form Data untuk file upload)
        data = request.get_json(silent=True)
        if not data:
            data = request.form.to_dict()

        letter_id = data.get('id')
        if not letter_id:
            return jsonify({"error": "ID surat wajib ada"}), 400

        # 2. KONVERSI TIPE DATA
        if 'is_decree' in data:
            if isinstance(data['is_decree'], str):
                data['is_decree'] = data['is_decree'].lower() == 'true'

        try:
            if 'classification_id' in data and data['classification_id']:
                data['classification_id'] = int(data['classification_id'])
        except ValueError:
             return jsonify({"error": "Classification ID harus angka"}), 400

        # 3. HANDLE FILE UPLOAD BARU
        file = request.files.get('file')
        if file:
            try:
                UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage', 'documents', 'outgoing_letters')
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)

                filename = secure_filename(file.filename)
                full_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(full_path)
                
                # Update path di database
                data['attachment_path'] = os.path.join('storage', 'documents', 'outgoing_letters', filename)
            except Exception as e:
                return jsonify({"error": f"Gagal upload file: {str(e)}"}), 500
        
        # 4. PROSES UPDATE DB
        db_session: Session = db.SessionLocal()
        try:
            updated_letter = update_outgoing_letter(db_session, letter_id, data)
            
            if not updated_letter:
                return jsonify({"error": "Letter not found"}), 404

            current_user = get_current_user_obj(db_session)
            if current_user:
                updated_fields = [k for k in data.keys() if k not in ['id', 'user_id']]
                fields_str = ", ".join(updated_fields)
                action = f"Pengguna '{current_user.username}' mengupdate ({fields_str}) surat keluar nomor: '{updated_letter.number}'."
                create_log(db_session, current_user.id, action)

            return jsonify(updated_letter.to_dict()), 200

        except ValueError as e:
            db_session.rollback()
            return jsonify({"error": str(e)}), 400
        finally:
            db_session.close()

    except Exception as e:
        print(f"Error Update Outgoing: {e}")
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

@outgoing_letter_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_outgoing_letter_route():
    """Deletes an outgoing letter record.

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
    """Retrieves all outgoing letters.

    Fetches a list of all outgoing letters currently stored in the database.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list of outgoing letter objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        letters = get_all_outgoing_letters(db_session)
        return jsonify([l.to_dict() for l in letters]), 200
    finally:
        db_session.close()

@outgoing_letter_bp.route('/get_by_keys', methods=['POST'])
def get_outgoing_by_keys_route():
    """Retrieves outgoing letters filtered by multiple keys.

    Allows advanced filtering using a dictionary of parameters.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): Dictionary of filter criteria.
            Example: {"destination": "Sekolah", "is_decree": true}

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
        letters = get_outgoing_letters_by_keys(db_session, filters)
        return jsonify([l.to_dict() for l in letters]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()