from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.report_card import create_report_card, update_report_card, delete_report_card, get_all_report_cards, get_report_cards_by_keys
from app.services.user import get_users_by_keys
from app.services.log import create_log
from app import db

report_card_bp = Blueprint('report_card', __name__)

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

@report_card_bp.route('/create', methods=['POST'])
@jwt_required()
def create_report_card_route():
    """Creates a new report card record.

    Requires a valid JWT access token. Date fields here are treated as strings.

    Args:
        No explicit arguments. Expects JSON payload:
        number (str): Unique report card number.
        student_name (str): Name of the student.
        class_name (str): The class name.
        academic_year (str): The academic year.
        attachment_path (str, optional): File path.

    Returns:
        tuple[Response, int]:
            * 201: JSON of the created report card.
            * 400: Missing fields.
            * 401: User authentication failed.
            * 409: Number already exists.
            * 500: Internal Server Error.
    """
    data = request.json
    required_fields = ['number', 'student_name', 'class_name', 'academic_year']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        current_user = get_current_user_obj(db_session)
        if not current_user:
            return jsonify({"error": "User authentication failed"}), 401

        new_report = create_report_card(db_session, data, user_id=current_user.id)
        
        try:
            action = f"Pengguna '{current_user.username}' menambahkan raport siswa '{new_report.student_name}' (No: {new_report.number})."
            create_log(db_session, current_user.id, action)
        except Exception as log_error:
            print(f"Log Error: {log_error}")

        return jsonify(new_report.to_dict()), 201

    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Nomor dokumen sudah terdaftar (harus unik)."}), 409
    except Exception as e:
        db_session.rollback()
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        db_session.close()

@report_card_bp.route('/update', methods=['POST'])
@jwt_required()
def update_report_card_route():
    """Updates an existing report card record."""
    data = request.json
    report_id = data.get('id')
    
    if not report_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated_report = update_report_card(db_session, report_id, data)
        
        if not updated_report:
            return jsonify({"error": "Report card not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            updated_fields = list(data.keys())
            if 'id' in updated_fields: updated_fields.remove('id')
            fields_str = ", ".join(updated_fields)
            
            action = f"Pengguna '{current_user.username}' mengupdate data ({fields_str}) pada raport nomor: '{updated_report.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(updated_report.to_dict()), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

@report_card_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_report_card_route():
    """
    Deletes a report card record by its ID.

    Requires a valid JWT access token. The action is logged to the database
    linking the deletion to the current user.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The unique identifier (primary key) of the report card.

    Returns:
        tuple[Response, int]:
            * 200: JSON dictionary of the deleted report card data.
            * 404: Error message if the report card ID is not found.
    """
    data = request.json
    report_id = data.get('id')

    db_session: Session = db.SessionLocal()
    try:
        deleted_report = delete_report_card(db_session, report_id)
        
        if not deleted_report:
            return jsonify({"error": "Report card not found"}), 404

        current_user = get_current_user_obj(db_session)
        if current_user:
            action = f"Pengguna '{current_user.username}' menghapus raport nomor: '{deleted_report.number}'."
            create_log(db_session, current_user.id, action)

        return jsonify(deleted_report.to_dict()), 200
    finally:
        db_session.close()

@report_card_bp.route('/get_all', methods=['GET'])
def get_all_report_cards_route():
    """
    Retrieves report card records filtered by specific criteria.

    Allows filtering based on multiple columns provided in the filters dictionary.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): A dictionary where keys represent column names and 
                        values represent the data to filter by.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list of report cards matching the filters.
            * 400: Error message if the 'filters' dictionary is missing, 
                   invalid, or contains invalid keys.
    """
    db_session: Session = db.SessionLocal()
    try:
        reports = get_all_report_cards(db_session)
        return jsonify([r.to_dict() for r in reports]), 200
    finally:
        db_session.close()

@report_card_bp.route('/get_by_keys', methods=['POST'])
def get_report_by_keys_route():
    """
    Retrieves report card records filtered by specific criteria.

    Allows filtering based on multiple columns provided in the filters dictionary.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): A dictionary where keys represent column names and 
                        values represent the data to filter by.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list of report cards matching the filters.
            * 400: Error message if the 'filters' dictionary is missing, 
                   invalid, or contains invalid keys.
    """
    data = request.json
    filters = data.get('filters')

    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        reports = get_report_cards_by_keys(db_session, filters)
        return jsonify([r.to_dict() for r in reports]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()