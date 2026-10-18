import io
import os

from werkzeug.datastructures import FileStorage

from app.utils.file_helper import delete_physical_file, handle_file_upload

def test_delete_physical_file_removes_uploaded_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    upload = FileStorage(stream=io.BytesIO(b"isi"), filename="surat.pdf")

    db_path, full_path = handle_file_upload(upload, "incoming_letters")
    assert os.path.exists(full_path)

    delete_physical_file(db_path)

    assert not os.path.exists(full_path)
