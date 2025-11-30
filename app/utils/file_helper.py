import os
import time

def cleanup_old_files(directory_path, file_extension, days_to_keep=7):
    """Removes files in a directory older than a specified number of days.

    Args:
        directory_path (str): The target directory to clean.
        file_extension (str): Filter files by extension (e.g., '.sql', '.log').
        days_to_keep (int): Retention period in days.
    """
    if not os.path.exists(directory_path):
        return

    now = time.time()
    cutoff = now - (days_to_keep * 86400)

    try:
        for f in os.listdir(directory_path):
            f_path = os.path.join(directory_path, f)
            
            # Cek apakah file dan ekstensinya cocok
            if os.path.isfile(f_path) and f.endswith(file_extension):
                if os.path.getmtime(f_path) < cutoff:
                    try:
                        os.remove(f_path)
                        print(f"[Maintenance] Deleted old file: {f}")
                    except OSError as e:
                        print(f"[Warning] Failed to delete {f}: {e}")
                        
    except Exception as e:
        print(f"[Error] cleanup_old_files failed: {e}")