"""Backup dan restore database SQLite beserta riwayatnya di file JSON.

Entri log berbentuk dict dari JSON, jadi isinya diberi tipe `Any`.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from typing import Any
from datetime import datetime
from app.core.database import engine
from app.errors import BackupError, RestoreError
from app.utils.file_helper import cleanup_old_files
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

BACKUP_DIR = os.path.join(os.getcwd(), 'database', 'backups')
LOG_FILE_PATH = os.path.join(BACKUP_DIR, 'backup_logs.json')
BACKUP_EXTENSION = '.db'

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

def _database_path() -> str:
    # Contoh: sqlite:///database/arsip.db -> "database/arsip.db"
    return engine.url.database

def _copy_database(source_path: str, target_path: str) -> None:
    # API backup sqlite3 menyalin halaman secara konsisten walau database sedang dibuka
    with closing(sqlite3.connect(source_path)) as source, closing(sqlite3.connect(target_path)) as target:
        source.backup(target)

def _create_backup_file(prefix: str) -> tuple[str, str]:
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    db_name = os.path.splitext(os.path.basename(_database_path()))[0]
    # Contoh: 2026-10-18_07-52-00
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{prefix}_{db_name}_{timestamp}{BACKUP_EXTENSION}"
    filepath = os.path.join(BACKUP_DIR, filename)

    try:
        _copy_database(_database_path(), filepath)
    except (sqlite3.Error, OSError):
        if os.path.exists(filepath):
            os.remove(filepath)
        raise
    return filename, filepath

def perform_database_backup(triggered_by: str = "SYSTEM") -> dict[str, str]:
    """Menyalin database aktif ke folder backup.

    Hasilnya dicatat ke log JSON, dan file `.db` yang lebih tua dari 7 hari
    dihapus.

    Args:
        triggered_by: Nama tampilan akun, atau `SYSTEM` untuk backup otomatis.

    Returns:
        Nama dan path file backup.

    Raises:
        BackupError: Kalau database gagal dibaca atau file backup gagal ditulis.
    """
    try:
        filename, filepath = _create_backup_file("backup")
    except (sqlite3.Error, OSError) as e:
        message = f"Backup gagal: {e}"
        logger.error(message, exc_info=True)
        _log_to_json(filename=None, status="FAILED", message=message, triggered_by=triggered_by)
        raise BackupError(message) from e

    cleanup_old_files(directory_path=BACKUP_DIR, file_extension=BACKUP_EXTENSION, days_to_keep=7)
    _log_to_json(filename=filename, status="SUCCESS",
                 message="Database backup created successfully.", triggered_by=triggered_by)
    return {"filename": filename, "path": filepath}

def _check_backup_file(filepath: str, filename: str) -> None:
    try:
        with closing(sqlite3.connect(filepath)) as conn:
            result = conn.execute("PRAGMA integrity_check").fetchone()[0]
    except sqlite3.DatabaseError as e:
        raise RestoreError(f"File '{filename}' bukan database SQLite yang valid.") from e
    if result != "ok":
        raise RestoreError(f"File '{filename}' rusak: {result}")

def perform_database_restore(filename: str) -> dict[str, str]:
    """Memulihkan database dari file backup.

    Sebelum menimpa, database aktif disalin sebagai `pre_restore_*.db` agar
    pemulihan yang salah pilih bisa dibatalkan.

    Args:
        filename: Nama file backup; hanya nama file yang dipakai, path diabaikan.

    Returns:
        Status dan pesan hasil pemulihan.

    Raises:
        FileNotFoundError: Kalau file backup tidak ada di folder backup.
        RestoreError: Kalau file backup tidak valid atau penyalinan gagal.
    """
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File backup '{safe_filename}' tidak ditemukan di server.")

    _check_backup_file(filepath, safe_filename)

    try:
        pre_restore_name, _ = _create_backup_file("pre_restore")
        _log_to_json(filename=pre_restore_name, status="SUCCESS",
                     message=f"Backup otomatis sebelum restore dari {safe_filename}.", triggered_by="SYSTEM")
        # Koneksi lama ditutup agar tidak ada yang memegang database saat ditimpa
        engine.dispose()
        _copy_database(filepath, _database_path())
    except (sqlite3.Error, OSError) as e:
        logger.error(f"Restore dari {safe_filename} gagal: {e}", exc_info=True)
        raise RestoreError(f"Proses Restore Gagal: {e}") from e

    return {
        "status": "SUCCESS",
        "message": f"Database berhasil dipulihkan dari {safe_filename}"
    }
