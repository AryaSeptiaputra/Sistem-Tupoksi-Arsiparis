import os
import tempfile

import pytest
from flask_jwt_extended import create_access_token

# Diset sebelum `app` di-import agar engine memakai SQLite sementara,
# bukan database dari .env.
_db_file = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_file}"
os.environ.setdefault("JWT_SECRET_KEY", "test_key_for_pytest_only_0123456789")
os.environ.setdefault("SECRET_KEY", "test_session_key_for_pytest_only")


@pytest.fixture
def auth_header():
    """Pembuat header Authorization untuk aplikasi Flask uji.

    Token dibuat tanpa claim `id`, sehingga log aktivitas dari request uji
    tercatat tanpa pelaku dan tidak butuh baris akun.
    """
    def build(app):
        with app.app_context():
            token = create_access_token(identity="uji")
        return {"Authorization": f"Bearer {token}"}
    return build
