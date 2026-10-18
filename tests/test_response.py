import pytest
from flask import Flask
from app.utils.response import handle_database_error

@pytest.fixture(autouse=True)
def app_context():
    with Flask(__name__).app_context():
        yield

@pytest.mark.parametrize("message, operation, status, expected", [
    ("UNIQUE constraint failed: incoming_letter.number", "menyimpan", 400, "Nomor dokumen sudah ada"),
    ("UNIQUE constraint failed: teacher.nuptk", "menyimpan", 400, "NUPTK sudah terdaftar"),
    ("UNIQUE constraint failed: storage_location.name", "menyimpan", 400, "sudah ada dalam sistem"),
    ("FOREIGN KEY constraint failed", "menghapus", 400, "masih digunakan oleh data lain"),
    ("FOREIGN KEY constraint failed", "menyimpan", 400, "Data terkait tidak ditemukan"),
    ("NOT NULL constraint failed: diploma.number", "memperbarui", 400, "field wajib"),
    ("disk I/O error", "memperbarui", 500, "Gagal memperbarui data"),
])
def test_sqlite_errors_map_to_user_messages(message, operation, status, expected):
    response, status_code = handle_database_error(Exception(f"(sqlite3.IntegrityError) {message}"), operation)

    assert status_code == status
    assert expected in response.get_json()["message"]
