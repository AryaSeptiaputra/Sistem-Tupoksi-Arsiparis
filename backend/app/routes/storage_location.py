from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.storage_location import (
    create_storage_location, 
    update_storage_location, 
    delete_storage_location, 
    get_all_storage_locations
)
from app import db

storage_location_bp = Blueprint('storage_location', __name__)

@storage_location_bp.route('/create', methods=['POST'])
@jwt_required()
def create_route():
    data = request.json
    if 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        new_loc = create_storage_location(db_session, data)
        return jsonify(new_loc.to_dict()), 201
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Storage name already exists"}), 409
    except Exception as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()

@storage_location_bp.route('/update', methods=['POST'])
@jwt_required()
def update_route():
    data = request.json
    loc_id = data.get('id')
    
    if not loc_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated = update_storage_location(db_session, loc_id, data)
        if not updated:
            return jsonify({"error": "Location not found"}), 404
        return jsonify(updated.to_dict()), 200
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Storage name conflict"}), 409
    finally:
        db_session.close()

@storage_location_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_route():
    data = request.json
    loc_id = data.get('id')
    
    db_session: Session = db.SessionLocal()
    try:
        deleted = delete_storage_location(db_session, loc_id)
        if not deleted:
            return jsonify({"error": "Location not found"}), 404
        return jsonify(deleted.to_dict()), 200
    finally:
        db_session.close()

@storage_location_bp.route('/get_all', methods=['GET'])
@jwt_required()
def get_all_route():
    db_session: Session = db.SessionLocal()
    try:
        locations = get_all_storage_locations(db_session)
        return jsonify([loc.to_dict() for loc in locations]), 200
    finally:
        db_session.close()