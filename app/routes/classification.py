from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.classification import Classification 
from app.services.classification import create_classification, update_classification, delete_classification, get_all_classifications, get_classification_by_key
from app import db

classification_bp = Blueprint('classification', __name__)

@classification_bp.route('/create', methods=['POST'])
@jwt_required()
def create_classification_route():
    """
    Creates a new letter classification.

    Request Body:
        name (str): The name of the classification.
        code (str): The unique code.

    Returns:
        JSON: The created classification object.
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

    Request Body:
        id (int): The ID of the classification to update.

    Returns:
        JSON: The updated classification object.
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

    Request Body:
        id (int): The ID of the classification to delete.

    Returns:
        JSON: The deleted classification data.
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

    Returns:
        JSON: A list of classification objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        classifications = get_all_classifications(db_session)
        return jsonify([cls.to_dict() for cls in classifications]), 200
    finally:
        db_session.close()

@classification_bp.route('/get_by_key', methods=['POST'])
def get_classification_by_key_route():
    """
    Retrieves classifications filtered by a specific key.

    Request Body:
        key (str): The column to filter by.
        value (str): The value to search.

    Returns:
        JSON: A list of matching classification objects.
    """
    data = request.json
    key = data.get('key')
    value = data.get('value')

    if not key or not value:
        return jsonify({"error": "Both 'key' and 'value' are required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        results = get_classification_by_key(db_session, key, value)
        
        if not results:
            return jsonify({"message": "Classification not found"}), 404

        return jsonify([item.to_dict() for item in results]), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()