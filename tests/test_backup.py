import os

import pytest
from app import create_app
from app.core.database import SessionLocal
from app.errors import RestoreError
from app.models.storage_location import StorageLocation
from app.services import backup

@pytest.fixture
def backup_dir(tmp_path, monkeypatch):
    create_app()
    monkeypatch.setattr(backup, "BACKUP_DIR", str(tmp_path))
    monkeypatch.setattr(backup, "LOG_FILE_PATH", str(tmp_path / "backup_logs.json"))
    yield tmp_path
    session = SessionLocal()
    session.query(StorageLocation).delete()
    session.commit()
    session.close()

def _add_location(name):
    session = SessionLocal()
    session.add(StorageLocation(name=name))
    session.commit()
    session.close()

def _location_names():
    session = SessionLocal()
    names = {location.name for location in session.query(StorageLocation).all()}
    session.close()
    return names

def test_restore_returns_data_to_backup_point(backup_dir):
    _add_location("Lemari A")
    result = backup.perform_database_backup(triggered_by="Uji")
    _add_location("Lemari B")

    backup.perform_database_restore(result["filename"])

    assert _location_names() == {"Lemari A"}
    assert result["filename"].endswith(".db")
    assert any(name.startswith("pre_restore_") for name in os.listdir(backup_dir))
    assert [log["status"] for log in backup.get_all_logs()] == ["SUCCESS", "SUCCESS"]

def test_restore_rejects_file_that_is_not_sqlite(backup_dir):
    (backup_dir / "rusak.db").write_text("bukan database")

    with pytest.raises(RestoreError, match="bukan database SQLite"):
        backup.perform_database_restore("rusak.db")

def test_restore_missing_file_raises_not_found(backup_dir):
    with pytest.raises(FileNotFoundError):
        backup.perform_database_restore("../tidak_ada.db")
