from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.classification import classification
from app.services.classification import create_classification, update_classification, delete_classification, get_all_classifications, get_classification_by_key
from app import db

classification_bp = Blueprint('classification', __name__)

@classification_bp.route('/create', methods=['POST'])
@jwt_required()
def create_classification_route():
    data = request.json

    required_fields = ['name', 'code']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        new_classification = create_classification(db_session, data)
        return jsonify(
            new_classification.to_dict()
        ), 201

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Classification with the same name or kode already exists"}), 409
    
    finally:
        db_session.close()

@classification_bp.route('/update', methods=['POST'])
@jwt_required()
def update_classification_route():
    data = request.json
    classification_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        updated_classification = update_classification(db_session, classification_id, data)
        if not updated_classification:
            return jsonify({"error": "Classification not found"}), 404

        return jsonify(
            updated_classification.to_dict()
        ), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Classification with the same name or kode already exists"}), 409
    
    finally:
        db_session.close()

@classification_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_classification_route():
    data = request.json
    classification_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_classification = delete_classification(db_session, classification_id)
        if not deleted_classification:
            return jsonify({"error": "Classification not found"}), 404

        return jsonify(
            deleted_classification.to_dict()
        ), 200

    finally:
        db_session.close()

@classification_bp.route('/get_all', methods=['GET'])
def get_all_classifications_route():
    db_session: Session = db.SessionLocal()
    try:
        classifications = get_all_classifications(db_session)
        return jsonify([cls.to_dict() for cls in classifications]), 200
    finally:
        db_session.close()

@classification_bp.route('/get_by_key', methods=['post'])
def get_classification_by_key_route():

    data=request.json

    key = data.get('key')
    value = data.get('value')

    if not key or not value:
        return jsonify({"error": "Both 'key' and 'value' are required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        classification_record = get_classification_by_key(db_session, key, value)
        if not classification_record:
            return jsonify({"error": "Classification not found"}), 404

        return jsonify(classification_record.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    finally:
        db_session.close()
