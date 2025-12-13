import os
from flask import Blueprint, send_from_directory, abort, jsonify

# Hapus import jwt_required karena file ini harus public accessible oleh browser
# from flask_jwt_extended import jwt_required 

storage_bp = Blueprint('storage', __name__)

@storage_bp.route('/<path:filename>', methods=['GET'])
# @jwt_required() <--- JANGAN GUNAKAN INI untuk route file statis via window.open
def serve_storage_file(filename):
    """
    Melayani file dari folder storage.
    URL Browser: domain.com/storage/documents/incoming_letters/namafile.pdf
    filename yg ditangkap: documents/incoming_letters/namafile.pdf
    """
    
    # 1. Tentukan Root Project & Folder Storage
    base_dir = os.getcwd()
    storage_folder = os.path.join(base_dir, 'storage')

    # 2. Gabungkan path
    full_path = os.path.join(storage_folder, filename)

    # 3. Validasi Keamanan (Mencegah user akses file di luar folder storage)
    if not os.path.commonprefix([full_path, storage_folder]) == storage_folder:
        return jsonify({"error": "Akses dilarang!"}), 403

    # 4. Cek keberadaan file
    if not os.path.exists(full_path):
        return jsonify({"error": "File fisik tidak ditemukan"}), 404

    # 5. Kirim File
    try:
        directory = os.path.dirname(full_path)
        file_name = os.path.basename(full_path)
        return send_from_directory(directory, file_name)
    except Exception as e:
        print(f"Storage Error: {e}")
        abort(404)