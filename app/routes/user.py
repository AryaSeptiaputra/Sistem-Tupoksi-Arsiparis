from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.user import create_user, update_user, delete_user, get_all_users, get_users_by_keys
from app.services.log import create_log
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/create', methods=['POST'])
@jwt_required()
def create_user_route():
    """
    Creates a new user in the system.

    Requires a valid JWT access token. Creates a user record and logs the
    action performed by the admin.

    Args:
        No explicit arguments. Expects JSON payload:
        nuptk (str): Unique ID (Nomor Unik Pendidik dan Tenaga Kependidikan).
        username (str): Unique username for login.
        password (str): Raw password (will be hashed by the service).
        role (str): Role of the user (e.g., 'headmaster', 'admin', 'teacher').
        status (str): Account status (e.g., 'active', 'inactive').

    Returns:
        tuple[Response, int]:
            * 201: JSON success message.
            * 400: Missing required fields.
            * 409: NUPTK or Username already exists.
            * 500: Internal Server Error.
    """
    data = request.json
    required_fields = ['nuptk', 'username', 'password', 'role', 'status']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400
    
    db_session: Session = db.SessionLocal()

    try:
        new_user = create_user(db_session, data)
        
        try:
            current_user_nuptk = get_jwt_identity()
            admin_users = get_users_by_keys(db_session, {'nuptk': current_user_nuptk})
            
            if admin_users:
                admin_user = admin_users[0]
                action = f"Pengguna membuat user baru dengan NUPTK: '{new_user.nuptk}'."
                create_log(db_session, admin_user.id, action)
        except Exception as e:
            print(f"Warning Log Error: {e}")

        return jsonify({
            "message": f"Berhasil membuat pengguna dengan nomor NUPTK: {new_user.nuptk}"
        }), 201
    
    except IntegrityError:
        db_session.rollback()
        return jsonify({"message": "Gagal: NUPTK atau Username sudah terdaftar."}), 409
    except Exception as e:
        db_session.rollback()
        print(f"Error Create User: {e}")
        return jsonify({"message": "Terjadi kesalahan internal server"}), 500
    finally:
        db_session.close()
    

@user_bp.route('/update', methods=['POST'])
@jwt_required()
def updated_user_route():
    """
    Updates an existing user's details.

    Requires a valid JWT access token. Updates the fields provided in the
    JSON payload and logs the changes.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the user to update (Required).
        ... (Any other field from create_user_route to update).

    Returns:
        tuple[Response, int]:
            * 200: JSON success message.
            * 400: Missing 'id' or validation error.
            * 404: User not found.
            * 409: Update causes duplicate NUPTK/Username.
    """
    data = request.json
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({"error": "ID is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        updated_user = update_user(db_session, user_id, data)
        if not updated_user:
            return jsonify({"error": "User not found"}), 404
        
        try:
            current_user_nuptk = get_jwt_identity()
            admin_users = get_users_by_keys(db_session, {'nuptk': current_user_nuptk})

            updated_fields = list(data.keys())
            if 'id' in updated_fields: updated_fields.remove('id')
            
            fields_str = ", ".join(updated_fields)

            if admin_users:
                action = f"Pengguna memperbarui data ({fields_str}) pengguna NUPTK: '{updated_user.nuptk}'."
                create_log(db_session, admin_users[0].id, action)

        except Exception as e:
            print(f"Warning Log Error: {e}")

        return jsonify({
            "message": f"Berhasil memperbarui data pengguna dengan NUPTK: {updated_user.nuptk}"
        }), 200

    except ValueError as e:
        db_session.rollback()
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        db_session.rollback()
        return jsonify({"error": "Username/NUPTK conflict"}), 409
    finally:
        db_session.close()

@user_bp.route('/delete', methods=['POST'])
@jwt_required()
def delete_user_route():
    """
    Deletes a user from the system.

    Requires a valid JWT access token. Removes the user record and logs
    the deletion.

    Args:
        No explicit arguments. Expects JSON payload:
        id (int): The ID of the user to delete.

    Returns:
        tuple[Response, int]:
            * 200: JSON success message and deleted user data.
            * 400: Missing 'id'.
            * 404: User not found.
    """
    data = request.json
    user_id = data.get('id')
    
    if not user_id:
        return jsonify({"error": "id is required"}), 400
    
    db_session: Session = db.SessionLocal()
    try:
        deleted_user = delete_user(db_session, user_id)
        if not deleted_user:
            return jsonify({"error": "User not found"}), 404
        
        try:
            current_user_nuptk = get_jwt_identity()
            admin_users = get_users_by_keys(db_session, 'nuptk', current_user_nuptk)
            if admin_users:
                create_log(db_session, admin_users[0].id, f"Menghapus user NUPTK: {deleted_user.nuptk}")
        except Exception:
            pass

        return jsonify({
            "message": f"Berhasil menghapus pengguna dengan NUPTK: {deleted_user.nuptk}",
            "data": deleted_user.to_dict()
        }), 200

    finally:
        db_session.close()

@user_bp.route('/get_all', methods=['GET'])
def get_all_users_route():
    """
    Retrieves a list of all users.

    Fetches all user records currently stored in the database.

    Returns:
        tuple[Response, int]:
            * 200: A JSON list of user objects.
    """
    db_session: Session = db.SessionLocal()
    try:
        users = get_all_users(db_session)
        return jsonify([user.to_dict() for user in users]), 200
    finally:
        db_session.close()

@user_bp.route('/get_by_keys', methods=['POST'])
def get_users_by_keys_route():
    """
    Retrieves users filtered by multiple keys.

    Allows filtering user lists based on specific criteria provided in the
    'filters' dictionary.

    Args:
        No explicit arguments. Expects JSON payload:
        filters (dict): Dictionary of filter criteria.
            Example: {"role": "admin", "status": "active"}

    Returns:
        tuple[Response, int]:
            * 200: A list of users matching the filters.
            * 400: Missing 'filters' dictionary or invalid format.
    """
    data = request.json
    filters = data.get('filters')
    
    if not filters or not isinstance(filters, dict):
        return jsonify({"error": "'filters' dictionary is required"}), 400

    db_session: Session = db.SessionLocal()
    try:
        users = get_users_by_keys(db_session, filters)
        return jsonify([user.to_dict() for user in users]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()