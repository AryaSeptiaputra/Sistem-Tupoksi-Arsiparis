import os
import tempfile

# Diset sebelum `app` di-import agar engine memakai SQLite sementara,
# bukan database dari .env.
_db_file = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file}"
os.environ.setdefault("JWT_SECRET_KEY", "test_key_for_pytest_only_0123456789")
os.environ.setdefault("SECRET_KEY", "test_session_key_for_pytest_only")
