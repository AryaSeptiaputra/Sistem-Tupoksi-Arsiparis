"""Backup dan restore database MySQL beserta riwayatnya di file JSON.

Entri log berbentuk dict dari JSON, jadi isinya diberi tipe `Any`.
"""

import json
import os
import subprocess
from typing import Any
from datetime import datetime
from app.core.config import settings
from app.errors import BackupError, RestoreError
from app.utils.db_helper import parse_db_url
from app.utils.file_helper import cleanup_old_files
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

BACKUP_DIR = os.path.join(os.getcwd(), 'database', 'backups')
LOG_FILE_PATH = os.path.join(BACKUP_DIR, 'backup_logs.json')

def perform_database_backup(triggered_by: str = "SYSTEM") -> dict[str, str]:
    """Membuat file backup database MySQL dengan `mysqldump`.

    Hasilnya dicatat ke log JSON, dan file `.sql` yang lebih tua dari 7 hari
    dihapus.

    Args:
        triggered_by: Nama tampilan akun, atau `SYSTEM` untuk backup otomatis.

    Returns:
        Nama dan path file backup.

    Raises:
        BackupError: Kalau `mysqldump` gagal atau tidak bisa dijalankan.
    """
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    db_config = parse_db_url(settings.DATABASE_URL)
    
    # Contoh: 2026-10-18_07-52-00
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"backup_{db_config['name']}_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    # Kata sandi lewat MYSQL_PWD supaya tidak terlihat di daftar proses
    env = os.environ.copy()
    env['MYSQL_PWD'] = db_config['password']

    command = [
        'mysqldump',
        '-h', db_config['host'],
        '-P', str(db_config['port']),
        '-u', db_config['user'],
        '--single-transaction',
        '--quick',
        f'--result-file={filepath}',
        db_config['name']
    ]

    status = "FAILED"
    message = ""
    result_data = {}

    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        
        status = "SUCCESS"
        message = "Database backup created successfully."
        result_data = {"filename": filename, "path": filepath}
        
        cleanup_old_files(directory_path=BACKUP_DIR, file_extension='.sql', days_to_keep=7)

    except subprocess.CalledProcessError as e:
        status = "FAILED"
        err_msg = e.stderr if e.stderr else str(e)
        message = f"Dump process failed: {err_msg}"
        logger.error(message, exc_info=True)
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError as e:
        status = "FAILED"
        message = f"Unexpected error: {str(e)}"
        logger.error(message, exc_info=True)

    _log_to_json(
        filename=filename if status == "SUCCESS" else None,
        status=status,
        message=message,
        triggered_by=triggered_by
    )

    if status == "FAILED":
        raise BackupError(message)

    return result_data

def perform_database_restore(filename: str) -> dict[str, str]:
    """Memulihkan database dari file backup dengan klien `mysql`.

    Args:
        filename: Nama file backup; hanya nama file yang dipakai, path diabaikan.

    Returns:
        Status dan pesan hasil pemulihan.

    Raises:
        FileNotFoundError: Kalau file backup tidak ada di folder backup.
        RestoreError: Kalau klien `mysql` gagal atau tidak bisa dijalankan.
    """
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File backup '{safe_filename}' tidak ditemukan di server.")

    db_config = parse_db_url(settings.DATABASE_URL)

    env = os.environ.copy()
    env['MYSQL_PWD'] = db_config['password']

    command = [
        'mysql',
        '-h', db_config['host'],
        '-P', str(db_config['port']),
        '-u', db_config['user'],
        db_config['name']
    ]

    try:
        with open(filepath, 'r') as input_file:
            subprocess.run(
                command, 
                stdin=input_file, 
                env=env, 
                check=True, 
                capture_output=True, 
                text=True
            )
            
        return {
            "status": "SUCCESS", 
            "message": f"Database berhasil dipulihkan dari {safe_filename}"
        }

    except subprocess.CalledProcessError as e:
        err_msg = e.stderr if e.stderr else str(e)
        logger.error(f"Restore dari {safe_filename} gagal: {err_msg}", exc_info=True)
        raise RestoreError(f"Proses Restore Gagal: {err_msg}") from e
    except OSError as e:
        logger.error(f"Restore dari {safe_filename} gagal: {e}", exc_info=True)
        raise RestoreError(f"Error Tidak Terduga: {str(e)}") from e

def _log_to_json(filename: str | None, status: str, message: str, triggered_by: str) -> None:
    log_entry = {
        # Detik sejak epoch dipakai sebagai id; backup tidak berjalan dua kali per detik
        "id": int(datetime.now().timestamp()),
        "filename": filename,
        "status": status,
        "message": message,
        "created_by": triggered_by,
        "created_at": datetime.now().isoformat()
    }
    
    logs = get_all_logs()
    # Entri terbaru di urutan pertama
    logs.insert(0, log_entry)

    try:
        with open(LOG_FILE_PATH, 'w') as f:
            json.dump(logs, f, indent=4)
    except OSError as e:
        logger.critical(f"Gagal menulis log JSON backup: {e}", exc_info=True)

def get_all_logs() -> list[dict[str, Any]]:
    """Membaca riwayat backup dari file log JSON.

    Returns:
        Entri log, terbaru lebih dulu; kosong bila file belum ada atau rusak.
    """
    if not os.path.exists(LOG_FILE_PATH):
        return []
    
    try:
        with open(LOG_FILE_PATH, 'r') as f:
            data = json.load(f)
            return data
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Log backup {LOG_FILE_PATH} tidak terbaca, dianggap kosong: {e}", exc_info=True)
        return []