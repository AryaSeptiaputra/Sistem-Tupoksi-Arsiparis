from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.classification import Classification 
from app.services.classification import create_classification, update_classification, delete_classification, get_all_classifications, get_classifications_by_keys
from app import db

classification_bp = Blueprint('classification', __name__)

@classification_bp.route('/create', methods=['POST'])
@jwt_required()
def create_classification_route():
    """
    Creates a new letter classification.

    Requires a valid JWT access token. This endpoint accepts a JSON payload
    containing the name and unique code for the new classification.

    Args:
        No explicit arguments. Expects JSON payload:
        name (str): The name of the classification.
        code (str): The unique code for the classification.

    Returns:
        tuple[Response, int]:
            * 201: JSON of the created classification object.
            * 400: Missing required fields or validation error.
            * 409: Classification name or code already exists.
    """
    data = request.json
    required_fields = ['name', 'code']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        new_classification = create_classification(db_session, data)
        return jsonify(new_classification.to_dict()), 201

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Classification name or code already exists"}), 409
    finally:
        db_session.close()

@classification_bp.route('/update', methods=['POST'])
@jwt_required()
def update_classification_route():
    """
    Updates an existing classification.

    Requires a valid JWT access token. Updates the fields provided in the
    JSON payload for the specified classification ID.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the classification to update (Required).
        name (str, optional): The new name.
        code (str, optional): The new code.

    Returns:
        tuple[Response, int]:
            * 200: JSON of the updated classification object.
            * 400: Missing 'id' or validation error.
            * 404: Classification not found.
            * 409: Update causes duplicate name or code.
    """
    data = request.json
    classification_id = data.get('id')
    
    if not classification_id:
        return jsonify({"error": "id is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated_classification = update_classification(db_session, classification_id, data)
        if not updated_classification:
            return jsonify({"error": "Classification not found"}), 404

        return jsonify(updated_classification.to_dict()), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Duplicate name or code"}), 409
    finally:
        db_session.close()

@classification_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_classification_route():
    """
    Deletes a classification record.

    Requires a valid JWT access token.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the classification to delete.

    Returns:
        tuple[Response, int]:
            * 200: JSON data of the deleted classification.
            * 404: Classification not found.
    """
    data = request.json
    classification_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_classification = delete_classification(db_session, classification_id)
        if not deleted_classification:
            return jsonify({"error": "Classification not found"}), 404

        return jsonify(deleted_classification.to_dict()), 200
    finally:
        db_session.close()

@classification_bp.route('/get_all', methods=['GET'])
def get_all_classifications_route():
    """
    Retrieves all classification records.

    Fetches a complete list of letter classifications available in the database.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list containing all classification objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        classifications = get_all_classifications(db_session)
        return jsonify([cls.to_dict() for cls in classifications]), 200
    finally:
        db_session.close()

@classification_bp.route('/get_by_keys', methods=['POST'])
def get_classifications_by_keys_route():
    """
    Retrieves classifications filtered by multiple keys.

    Allows filtering the classification list based on specific criteria
    provided in the 'filters' dictionary.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): A dictionary of key-value pairs to filter by.
            Example: {"code": "A1", "name": "Umum"}

    Returns:
        tuple[Response, int]:
            * 200: A list of classifications matching the filters.
            * 400: Missing 'filters' dictionary or invalid format.
    """
    data = request.json
    filters = data.get('filters')

    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        results = get_classifications_by_keys(db_session, filters)
        return jsonify([item.to_dict() for item in results]), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()