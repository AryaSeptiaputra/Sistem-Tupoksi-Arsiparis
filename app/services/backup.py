import os
import subprocess
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.backup import Backup

from app.utils.db_helper import parse_db_url
from app.utils.file_helper import cleanup_old_files

BACKUP_DIR = os.path.join(os.getcwd(), 'database', 'backups')

def perform_database_backup(user_id=None):
    """Executes a MySQL database backup and orchestrates the cleanup and logging process.

    This function performs the following steps:
    1. Ensures the backup directory exists.
    2. Parses database credentials from the application settings.
    3. Executes `mysqldump` in a subprocess using secure environment variables.
    4. Cleans up old backup files based on the retention policy (7 days).
    5. Logs the operation result (Success/Failure) to the database.

    Args:
        user_id (int, optional): The ID of the user triggering the backup.
            Defaults to None, which implies a system-triggered automation.

    Returns:
        dict: A dictionary containing the backup details if successful.
            Example: ``{"filename": "backup_db_2023.sql", "path": "/abs/path/to/file"}``

    Raises:
        Exception: If the backup process fails (e.g., mysqldump error),
            an exception is raised with the specific error message after logging.
    """
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    db_config = parse_db_url(settings.DATABASE_URL)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"backup_{db_config['name']}_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

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
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        status = "FAILED"
        message = f"Unexpected error: {str(e)}"

    _log_to_database(filename=filename if status == "SUCCESS" else None,
                     status=status,
                     message=message,
                     user_id=user_id)

    if status == "FAILED":
        raise Exception(message)

    return result_data

def _log_to_database(filename, status, message, user_id):
    """Persists the backup operation log to the database using a fresh session.

    This helper function manages its own database session (`SessionLocal`) to ensure
    transaction isolation from the main request flow. It handles commit/rollback
    logic internally to prevent database locks or inconsistent states.

    Args:
        filename (str | None): The name of the created backup file. Pass None if failed.
        status (str): The outcome status (e.g., 'SUCCESS', 'FAILED').
        message (str): A descriptive message or error details.
        user_id (int | None): The ID of the user who initiated the backup.

    Returns:
        None
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