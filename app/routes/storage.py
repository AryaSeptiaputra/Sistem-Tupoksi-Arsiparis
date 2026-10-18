import os
from flask import Blueprint, send_from_directory, abort, jsonify
from flask.typing import ResponseReturnValue

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

storage_bp = Blueprint('storage', __name__)

# Sengaja tanpa jwt_required: file dibuka browser lewat window.open, yang
# tidak mengirim header Authorization.
@storage_bp.route('/<path:filename>', methods=['GET'])
def serve_storage_file(filename: str) -> ResponseReturnValue:
    """Mengirim file lampiran dari folder `storage`.

    Contoh: URL `/storage/documents/incoming_letters/a.pdf` menangkap
    `filename` = `documents/incoming_letters/a.pdf`.

    Args:
        filename: Path file relatif terhadap folder `storage`.

    Returns:
        File yang diminta, 403 bila path keluar dari folder `storage`, atau
        404 bila file tidak ada.
    """
    base_dir = os.getcwd()
    storage_folder = os.path.join(base_dir, 'storage')
    full_path = os.path.join(storage_folder, filename)

    # Menolak path yang keluar dari folder storage
    if not os.path.commonprefix([full_path, storage_folder]) == storage_folder:
        return jsonify({"error": "Akses dilarang!"}), 403

    if not os.path.exists(full_path):
        return jsonify({"error": "File fisik tidak ditemukan"}), 404

    try:
        directory = os.path.dirname(full_path)
        file_name = os.path.basename(full_path)
        return send_from_directory(directory, file_name)
    except Exception as e:
        logger.error(f"Gagal mengirim file storage: {e}", exc_info=True)
        abort(404)
