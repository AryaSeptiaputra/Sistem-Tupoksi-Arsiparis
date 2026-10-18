import os
import time
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.errors import FileStorageError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# 10 MB dalam byte
MAX_FILE_SIZE = 10 * 1024 * 1024

def cleanup_old_files(directory_path: str, file_extension: str, days_to_keep: int = 7) -> None:
    """Menghapus file berekstensi tertentu yang lebih tua dari batas hari.

    Kegagalan menghapus dicatat ke log tanpa menghentikan proses.

    Args:
        directory_path: Folder yang dibersihkan.
        file_extension: Ekstensi file yang diperiksa, misalnya `.sql`.
        days_to_keep: Umur maksimal file dalam hari.
    """
    if not os.path.exists(directory_path):
        return

    now = time.time()
    # 86400 detik = 1 hari
    cutoff = now - (days_to_keep * 86400)

    try:
        for f in os.listdir(directory_path):
            f_path = os.path.join(directory_path, f)
            if os.path.isfile(f_path) and f.endswith(file_extension):
                if os.path.getmtime(f_path) < cutoff:
                    try:
                        os.remove(f_path)
                    except OSError as e:
                        logger.warning(f"File lama {f_path} gagal dihapus: {e}", exc_info=True)
    except OSError as e:
        logger.error(f"cleanup_old_files gagal: {e}", exc_info=True)

def delete_physical_file(relative_path: str | None) -> None:
    """Menghapus file lampiran dari disk bila ada.

    Kegagalan menghapus dicatat ke log tanpa melempar error.

    Args:
        relative_path: Path yang tersimpan di database, misalnya
            `storage/documents/outgoing_letters/abc.pdf`.
    """
    if not relative_path:
        return

    try:
        # normpath merapikan `..` dan pemisah path sebelum digabung
        normalized_path = os.path.normpath(relative_path)
        full_path = os.path.join(os.getcwd(), normalized_path)

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"File berhasil dihapus: {full_path}")
        else:
            logger.warning(f"File tidak ditemukan untuk dihapus: {full_path}")

    except OSError as e:
        logger.error(f"Gagal menghapus file fisik: {e}", exc_info=True)

def handle_file_upload(file_obj: FileStorage | None, subfolder: str) -> tuple[str | None, str | None]:
    """Menyimpan file unggahan dengan nama acak UUID.

    Args:
        file_obj: File dari `request.files`.
        subfolder: Nama folder kategori, misalnya `incoming_letters`.

    Returns:
        Pasangan (path untuk database, path lengkap di disk), atau
        `(None, None)` bila tidak ada file.

    Raises:
        ValueError: Kalau ukuran file melebihi 10 MB.
        FileStorageError: Kalau folder atau file gagal ditulis ke disk.
    """
    if not file_obj:
        return None, None

    original_filename = secure_filename(file_obj.filename)
    # Contoh: ".pdf"
    file_extension = os.path.splitext(original_filename)[1].lower()

    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise ValueError(f"Ukuran file terlalu besar ({size_mb:.2f} MB). Maksimal file yang diperbolehkan adalah 10 MB.")

    # Contoh: "3f2a9c0e8b7d4e1fa6c5b4d3e2f1a0b9.pdf"
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    base_upload_dir = os.path.join(os.getcwd(), 'storage', 'documents', subfolder)

    full_path = os.path.join(base_upload_dir, unique_filename)
    try:
        if not os.path.exists(base_upload_dir):
            os.makedirs(base_upload_dir)
        file_obj.save(full_path)
    except OSError as e:
        logger.error(f"Gagal menyimpan file ke {full_path}: {e}", exc_info=True)
        raise FileStorageError(f"Gagal menyimpan file: {e}") from e

    # Garis miring "/" dipakai agar path bisa langsung dipakai sebagai URL
    db_path = f"storage/documents/{subfolder}/{unique_filename}"

    return db_path, full_path
