from flask import Blueprint, jsonify, request
from app.services.master_reference import MasterReferenceService

# Inisialisasi Blueprint
reference_bp = Blueprint('reference', __name__)
service = MasterReferenceService()

# ---------------------------------------------------
# PUBLIC / READ ONLY (Untuk Mengisi Dropdown)
# ---------------------------------------------------

@reference_bp.route('/api/references/<category>', methods=['GET'])
def get_options(category):
    """
    Contoh URL: /api/references/school_major
    Return: JSON Array opsi jurusan
    """
    try:
        # Ambil query param ?all=true jika ingin menampilkan yang tidak aktif (untuk menu admin)
        show_all = request.args.get('all') == 'true'
        
        results = service.get_by_category(category, only_active=not show_all)
        return jsonify({
            "status": "success",
            "data": results
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@reference_bp.route('/api/references/categories', methods=['GET'])
def get_categories():
    """
    Mendapatkan daftar Enum kategori yang tersedia.
    """
    return jsonify({
        "status": "success",
        "data": service.get_all_categories()
    })

# ---------------------------------------------------
# ADMIN ONLY (Create, Update, Delete)
# ---------------------------------------------------

@reference_bp.route('/api/references', methods=['POST'])
def create_option():
    """
    Menambah opsi baru.
    Body JSON: { "category": "school_major", "code": "DKV", "name": "Desain Komunikasi Visual" }
    """
    try:
        data = request.json
        if not data.get('category') or not data.get('code') or not data.get('name'):
            return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400

        result = service.create(data)
        return jsonify({"status": "success", "data": result}), 201
    except ValueError as ve:
         return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@reference_bp.route('/api/references/<int:id>', methods=['PUT'])
def update_option(id):
    """
    Update opsi.
    Body JSON: { "name": "Nama Baru", "sort_order": 5 }
    """
    try:
        data = request.json
        result = service.update(id, data)
        if not result:
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
            
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@reference_bp.route('/api/references/<int:id>', methods=['DELETE'])
def delete_option(id):
    """
    Menonaktifkan opsi (Soft Delete).
    """
    try:
        success = service.delete(id)
        if not success:
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404
            
        return jsonify({"status": "success", "message": "Opsi berhasil dinonaktifkan"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500