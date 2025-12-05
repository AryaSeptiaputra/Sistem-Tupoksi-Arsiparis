import os
import time
from werkzeug.utils import secure_filename

def cleanup_old_files(directory_path, file_extension, days_to_keep=7):
    """Menghapus file lama berdasarkan umur file."""
    if not os.path.exists(directory_path):
        return

    now = time.time()
    cutoff = now - (days_to_keep * 86400)

    try:
        for f in os.listdir(directory_path):
            f_path = os.path.join(directory_path, f)
            if os.path.isfile(f_path) and f.endswith(file_extension):
                if os.path.getmtime(f_path) < cutoff:
                    try:
                        os.remove(f_path)
                    except OSError:
                        pass
    except Exception as e:
        print(f"[Error] cleanup_old_files failed: {e}")

def delete_physical_file(relative_path):
    """Menghapus file fisik dari penyimpanan jika ada."""
    if not relative_path:
        return
    
    try:
        normalized_path = os.path.normpath(relative_path)
        full_path = os.path.join(os.getcwd(), normalized_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"File berhasil dihapus: {full_path}")
    except OSError as e:
        print(f"Gagal menghapus file fisik: {e}")

def handle_file_upload(file_obj, subfolder):
    """
    Menangani logika upload file secara terpusat.
    
    Args:
        file_obj: Object file dari request.files
        subfolder (str): Nama folder di dalam 'storage/documents/'
        
    Returns:
        tuple: (db_relative_path, full_system_path)
    """
    if not file_obj:
        return None, None
        
    # Tentukan folder tujuan
    upload_dir = os.path.join(os.getcwd(), 'storage', 'documents', subfolder)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # Amankan nama file dan simpan
    filename = secure_filename(file_obj.filename)
    full_path = os.path.join(upload_dir, filename)
    file_obj.save(full_path)
    
    # Path untuk disimpan di database
    db_path = os.path.join('storage', 'documents', subfolder, filename)
    
    return db_path, full_path