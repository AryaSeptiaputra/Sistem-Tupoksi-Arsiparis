import os
import time
import uuid  # [BARU] Untuk generate nama unik
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
    """
    Menghapus file fisik dari penyimpanan jika ada.
    Arg: relative_path (contoh: 'storage/documents/outgoing/abc.pdf')
    """
    if not relative_path:
        return
    
    try:
        # Normalisasi path untuk mencegah traversal
        normalized_path = os.path.normpath(relative_path)
        
        # [UPDATE] Arahkan ke folder static aplikasi
        # Asumsi struktur: root/app/static/storage/...
        full_path = os.path.join(os.getcwd(), 'app', 'static', normalized_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"File berhasil dihapus: {full_path}")
        else:
            print(f"File tidak ditemukan untuk dihapus: {full_path}")
            
    except OSError as e:
        print(f"Gagal menghapus file fisik: {e}")

def handle_file_upload(file_obj, subfolder):
    """
    Menangani logika upload file secara terpusat dengan RENAME UUID.
    
    Args:
        file_obj: Object file dari request.files
        subfolder (str): Nama folder kategori (misal: 'incoming_letters')
        
    Returns:
        tuple: (db_relative_path, full_system_path)
        
    Raises:
        ValueError: Jika ukuran file melebihi 10 MB
    """
    if not file_obj:
        return None, None
        
    # 1. Amankan nama file asli & Ambil Ekstensi
    original_filename = secure_filename(file_obj.filename)
    file_extension = os.path.splitext(original_filename)[1].lower() # .pdf, .jpg, dll

    # 2. Validasi Ukuran File (Maksimal 10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB dalam bytes
    file_obj.seek(0, os.SEEK_END)  # Pindah ke akhir file
    file_size = file_obj.tell()  # Dapatkan ukuran file
    file_obj.seek(0)  # Kembali ke awal
    
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise ValueError(f"Ukuran file terlalu besar ({size_mb:.2f} MB). Maksimal file yang diperbolehkan adalah 10 MB.")

    # 3. [BARU] Generate Nama Unik (UUID)
    # Contoh hasil: 'a1b2c3d4-1234-5678.pdf'
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"

    # 4. Tentukan folder tujuan (Masuk ke app/static agar bisa diakses browser)
    # Struktur: /app/static/storage/documents/{subfolder}/
    base_upload_dir = os.path.join(os.getcwd(), 'storage', 'documents', subfolder)
    
    if not os.path.exists(base_upload_dir):
        os.makedirs(base_upload_dir)

    # 5. Simpan File dengan Nama Baru
    full_path = os.path.join(base_upload_dir, unique_filename)
    file_obj.save(full_path)
    
    # 6. Path untuk Database (Relative terhadap folder static)
    # Menggunakan forward slash (/) agar kompatibel dengan URL HTML
    db_path = f"storage/documents/{subfolder}/{unique_filename}"
    
    return db_path, full_path