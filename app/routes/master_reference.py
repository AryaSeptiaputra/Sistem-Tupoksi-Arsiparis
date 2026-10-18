from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue
from app.services.master_reference import MasterReferenceService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

reference_bp = Blueprint('reference', __name__)
service = MasterReferenceService()


@reference_bp.route('/api/references/<category>', methods=['GET'])
def get_options(category: str) -> ResponseReturnValue:
    """Mengambil opsi satu kategori untuk dropdown.

    Args:
        category: Nilai kategori, misalnya `school_major`.

    Returns:
        200 dengan daftar opsi, atau 500 bila terjadi error.
    """
    try:
        # ?all=true ikut menampilkan opsi yang tidak aktif
        show_all = request.args.get('all') == 'true'

        results = service.get_by_category(category, only_active=not show_all)
        return jsonify({
            "status": "success",
            "data": results
        }), 200
    except Exception as e:
        logger.error(f"Gagal mengambil referensi {category}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@reference_bp.route('/api/references', methods=['POST'])
def create_option() -> ResponseReturnValue:
    """Menambah opsi referensi.

    Body JSON: `category`, `code`, `name`, dan kolom opsional.

    Returns:
        201 dengan opsi baru, 400 bila isian kurang atau kategori tidak
        valid, atau 500 bila terjadi error.
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
        logger.error(f"Gagal menambah referensi: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@reference_bp.route('/api/references/<int:id>', methods=['PUT'])
def update_option(id: int) -> ResponseReturnValue:
    """Mengubah opsi referensi.

    Args:
        id: Id opsi.

    Returns:
        200 dengan opsi setelah diubah, 404 bila tidak ditemukan, atau 500
        bila terjadi error.
    """
    try:
        data = request.json
        result = service.update(id, data)
        if not result:
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404

        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        logger.error(f"Gagal mengubah referensi {id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@reference_bp.route('/api/references/<int:id>', methods=['DELETE'])
def delete_option(id: int) -> ResponseReturnValue:
    """Menonaktifkan opsi referensi tanpa menghapus barisnya.

    Args:
        id: Id opsi.

    Returns:
        200 bila dinonaktifkan, 404 bila tidak ditemukan, atau 500 bila
        terjadi error.
    """
    try:
        success = service.delete(id)
        if not success:
            return jsonify({"status": "error", "message": "Data tidak ditemukan"}), 404

        return jsonify({"status": "success", "message": "Opsi berhasil dinonaktifkan"}), 200
    except Exception as e:
        logger.error(f"Gagal menonaktifkan referensi {id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
