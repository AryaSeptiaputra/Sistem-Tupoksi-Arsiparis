import pytest
from app import create_app
from app.core.database import SessionLocal
from app.errors import DataInUseError
from app.models.classification import Classification
from app.models.finance_archive import FinanceArchive
from app.models.storage_location import StorageLocation
from app.services.storage_location import delete_storage_location

@pytest.fixture
def db():
    create_app()
    session = SessionLocal()
    yield session
    for model in (FinanceArchive, Classification, StorageLocation):
        session.query(model).delete()
    session.commit()
    session.close()

def _location(db, name):
    location = StorageLocation(name=name)
    db.add(location)
    db.commit()
    return location

def test_delete_unused_location(db):
    location = _location(db, "Rak Kosong")

    assert delete_storage_location(db, location.id) is not None
    assert db.query(StorageLocation).filter_by(name="Rak Kosong").first() is None

def test_delete_location_used_by_archive_is_rejected(db):
    location = _location(db, "Rak Terisi")
    classification = Classification(name="Sekolah", code="421", retention_active_period=2,
                                    retention_inactive_period=5, final_action="permanent")
    db.add(classification)
    db.commit()
    db.add(FinanceArchive(title="SPJ", fiscal_year=2026, category="BOS_REG", amount=1,
                          classification_id=classification.id, storage_location_id=location.id))
    db.commit()

    with pytest.raises(DataInUseError, match="1 arsip"):
        delete_storage_location(db, location.id)

    db.rollback()
    archive = db.query(FinanceArchive).filter_by(title="SPJ").one()
    assert archive.storage_location_id == location.id
