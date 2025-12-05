import os
import subprocess
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.backup import Backup

from app.utils.db_helper import parse_db_url
from app.utils.file_helper import cleanup_old_files

# Mendefinisikan lokasi folder backup
BACKUP_DIR = os.path.join(os.getcwd(), 'database', 'backups')

def perform_database_backup(user_id=None):
    """
    Melakukan backup database MySQL menggunakan mysqldump.
    """
    
    # 1. Pastikan folder backup ada
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    db_config = parse_db_url(settings.DATABASE_URL)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"backup_{db_config['name']}_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    # 2. Siapkan environment variable untuk password (agar aman dan tidak muncul di ps aux)
    env = os.environ.copy()
    env['MYSQL_PWD'] = db_config['password']

    # 3. Perintah mysqldump
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
        
        # Hapus file lama (keep 7 hari)
        cleanup_old_files(directory_path=BACKUP_DIR, file_extension='.sql', days_to_keep=7)

    except subprocess.CalledProcessError as e:
        status = "FAILED"
        err_msg = e.stderr if e.stderr else str(e)
        message = f"Dump process failed: {err_msg}"
        # Hapus file kosong/corrupt jika ada
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        status = "FAILED"
        message = f"Unexpected error: {str(e)}"

    # 4. Simpan log ke database
    _log_to_database(
        filename=filename if status == "SUCCESS" else None,
        status=status,
        message=message,
        user_id=user_id
    )

    if status == "FAILED":
        raise Exception(message)

    return result_data

def perform_database_restore(filename):
    """
    Merestore database dari file SQL tertentu.
    PERINGATAN: Data lama akan tertimpa.
    """
    # 1. Validasi path file (security)
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(BACKUP_DIR, safe_filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File backup '{safe_filename}' tidak ditemukan di server.")

    db_config = parse_db_url(settings.DATABASE_URL)

    env = os.environ.copy()
    env['MYSQL_PWD'] = db_config['password']

    # 2. Perintah mysql untuk restore
    # mysql -h ... -u ... dbname
    command = [
        'mysql',
        '-h', db_config['host'],
        '-P', str(db_config['port']),
        '-u', db_config['user'],
        db_config['name']
    ]

    try:
        # Buka file SQL dan alirkan ke stdin proses mysql
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
        raise Exception(f"Proses Restore Gagal: {err_msg}")
    except Exception as e:
        raise Exception(f"Error Tidak Terduga: {str(e)}")

def _log_to_database(filename, status, message, user_id):
    """
    Helper function untuk menyimpan log backup ke DB dengan session terpisah.
    """
    session = SessionLocal()
    try:
        new_log = Backup(
            filename=filename,
            status=status,
            message=message,
            user_id=user_id
        )
        session.add(new_log)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"CRITICAL: Failed to save backup log. Error: {e}")
    finally:
        session.close()