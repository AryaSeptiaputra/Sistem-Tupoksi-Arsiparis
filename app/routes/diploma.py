import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from app.services.diploma import (
    create_diploma, 
    update_diploma, 
    delete_diploma, 
    get_all_diplomas, 
    get_diplomas_by_keys
)

from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db

diploma_bp = Blueprint('diploma', __name__)

@diploma_bp.route('/view', methods=['GET'])
def diploma_page():
    """
    Menampilkan halaman manajemen Ijazah (Frontend).
    URL: http://localhost:5000/diploma/view
    """
    return render_template('diploma.html')

def get_current_user_obj(db_session: Session):
    """Helper function to retrieve the currently logged-in user object.

    Uses the JWT identity (NUPTK/ID) from the request context to fetch
    the full User object from the database using the service with a filter.

    Args:
        db_session (Session): The active database session.

    Returns:
        User | None: The User object if found, otherwise None.
    """
    current_identity = get_jwt_identity()
    users = get_users_by_keys(db_session, {'nuptk': current_identity})
    return users[0] if users else None

@diploma_bp.route('/create', methods=['POST'])
@jwt_required()
def create_diploma_route():
    """Creates a new diploma (Ijazah) record with an optional file attachment.

    Requires a valid JWT access token. Accepts multipart/form-data to handle
    text fields and an optional file upload (scan of the diploma).
    
    Args:
        No explicit arguments. Expects Multipart/Form-Data payload:
        number (str): The serial number of the diploma (must be unique).
        student_name (str): The full name of the student.
        major (str): The vocational major (Kompetensi Keahlian), e.g., 'TKJ'.
        academic_year (str): The graduation year, e.g., '2024/2025'.
        is_collected (str|bool): 'true' if the diploma is physically collected.
        file (FileStorage, optional): The scanned document file.

    Returns:
        tuple[Response, int]:
            * 201: JSON of the created diploma including attachment path.
            * 400: Missing required fields or invalid data.
            * 401: User authentication failed.
            * 500: Internal Server Error or File Save Error.
    """
    data = request.form.to_dict()
    
    if 'is_collected' in data:
        if isinstance(data['is_collected'], str):
            data['is_collected'] = data['is_collected'].lower() == 'true'

    required_fields = ['number', 'student_name', 'major', 'academic_year']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'storage', 'documents', 'diplomas')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file = request.files.get('file')
    full_path = None 
    
    if file:
        try:
            filename = secure_filename(file.filename)
            full_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(full_path)
            
            data['attachment_path'] = os.path.join('storage', 'documents', 'diplomas', filename)
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            if full_path and os.path.exists(full_path):
                os.remove(full_path)
            return jsonify({"error": "User authentication failed"}), 401

        new_diploma = create_diploma(db_session, data, user_id=current_user.id)
        
        try:
            action = f"Pengguna '{current_user.username}' menambahkan ijazah No: '{new_diploma.number}' atas nama '{new_diploma.student_name}'."
            create_log(db_session, current_user.id, action)
        except Exception:
            pass

        return jsonify(new_diploma.to_dict()), 201

    except Exception as e:
        db_session.rollback()

        if full_path and os.path.exists(full_path):
            os.remove(full_path)
            
        print(f"Error Create Diploma: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@diploma_bp.route('/update', methods=['POST'])
@jwt_required()
def update_diploma_route():
    """Updates an existing diploma record.

    Requires a valid JWT access token. Updates specific fields provided in
    the JSON payload and logs the update activity.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the diploma to update (Required).
        student_name (str, optional): Updated name.
        major (str, optional): Updated major.
        is_collected (bool, optional): Update collection status.
        ... (Any other field from create_diploma_route).

    Returns:
        tuple[Response, int]:
            * 200: JSON of the updated diploma.
            * 400: Missing 'id' or validation error.
            * 404: Diploma not found.
    """
    data = request.json
    diploma_id = data.get('id')
    
    if not diploma_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated_diploma = update_diploma(db_session, diploma_id, data)
        
        if not updated_diploma:
            return jsonify({"error": "Diploma not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            updated_fields = list(data.keys())
            if 'id' in updated_fields: updated_fields.remove('id')
            fields_str = ", ".join(updated_fields)
            action = f"Pengguna '{current_user.username}' mengupdate ({fields_str}) pada ijazah No: '{updated_diploma.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(updated_diploma.to_dict()), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

@diploma_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_diploma_route():
    """Deletes a diploma record.

    Requires a valid JWT access token. Removes the record from the database
    and logs the deletion activity.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the diploma to delete.

    Returns:
        tuple[Response, int]:
            * 200: JSON data of the deleted diploma.
            * 404: Diploma not found.
    """
    data = request.json
    diploma_id = data.get('id')

    db_session: Session = db.SessionLocal()
    try:
        deleted_diploma = delete_diploma(db_session, diploma_id)
        
        if not deleted_diploma:
            return jsonify({"error": "Diploma not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            action = f"Pengguna '{current_user.username}' menghapus ijazah No: '{deleted_diploma.number}' milik '{deleted_diploma.student_name}'."
            create_log(db_session, current_user.id, action)

        return jsonify(deleted_diploma.to_dict()), 200
    finally:
        db_session.close()

@diploma_bp.route('/get_all', methods=['GET'])
def get_all_diplomas_route():
    """Retrieves all diploma records.

    Fetches a list of all diplomas currently stored in the database.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list of diploma objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        diplomas = get_all_diplomas(db_session)
        return jsonify([d.to_dict() for d in diplomas]), 200
    finally:
        db_session.close()

@diploma_bp.route('/get_by_keys', methods=['POST'])
def get_diplomas_by_keys_route():
    """Retrieves diploma records filtered by multiple keys.

    Allows advanced filtering using a dictionary of parameters.
    Example: Filtering for all diplomas in 'TKJ' major that are NOT collected yet.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): Dictionary of filter criteria.
            Example: {"major": "TKJ", "is_collected": false}

    Returns:
        tuple[Response, int]:
            * 200: A list of diplomas matching the filters.
            * 400: Missing 'filters' dictionary or invalid format.
    """
    data = request.json
    filters = data.get('filters')

    if not filters or not isinstance(filters, dict):
        # Fallback to direct dict check if wrapper key 'filters' is missing
        if data and isinstance(data, dict):
             filters = data
        else:
             return jsonify({"error": "'filters' dictionary is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        diplomas = get_diplomas_by_keys(db_session, filters)
        return jsonify([d.to_dict() for d in diplomas]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()