from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import Session
from app.services.log import get_all_logs, get_logs_paginated, get_logs_by_keys
from app import db

log_bp = Blueprint('log', __name__)

@log_bp.route('/get_all', methods=['GET'])
@jwt_required()
def get_all_logs_route():
    """
    Retrieves all activity logs with pagination.

    Requires a valid JWT access token. Fetches the complete history of
    system activities recorded in the database.

    Query Parameters:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 10, max: 100)

    Returns:
        tuple[Response, int]:
            * 200: A JSON object containing paginated log data.
            * 400: Invalid pagination parameters.
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        if page < 1 or per_page < 1 or per_page > 100:
            return jsonify({"error": "Invalid page or per_page parameters"}), 400
    except ValueError:
        return jsonify({"error": "Page and per_page must be integers"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        result = get_logs_paginated(db_session, page=page, per_page=per_page)
        return jsonify({
            'logs': [l.to_dict() for l in result['logs']],
            'pagination': {
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'total_pages': result['total_pages']
            }
        }), 200
    finally:
        db_session.close()

@log_bp.route('/get_by_keys', methods=['POST'])
@jwt_required()
def get_logs_by_keys_route():
    """
    Retrieves logs filtered by multiple keys.

    Requires a valid JWT access token. Allows filtering the logs based on
    specific criteria provided in the 'filters' dictionary.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): A dictionary of key-value pairs to filter by.
            Example: {"user_id": 1, "action": "LOGIN"}

    Returns:
        tuple[Response, int]:
            * 200: A list of logs matching the filters.
            * 400: Missing 'filters' dictionary or invalid format.
    """
    data = request.json
    filters = data.get('filters')

    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        logs = get_logs_by_keys(db_session, filters)
        return jsonify([l.to_dict() for l in logs]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()