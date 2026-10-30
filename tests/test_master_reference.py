import pytest
from app import create_app
from app.core.database import SessionLocal
from app.models.master_reference import MasterReference
from app.services.master_reference import MasterReferenceService

@pytest.fixture
def service():
    create_app()
    yield MasterReferenceService()
    db = SessionLocal()
    db.query(MasterReference).delete()
    db.commit()
    db.close()

def test_create_is_active_by_default(service):
    created = service.create({"category": "finance_category", "code": "uji_aktif", "name": "Uji Aktif"})

    assert created["is_active"] is True

def test_create_keeps_inactive_choice(service):
    created = service.create({"category": "finance_category", "code": "uji_nonaktif", "name": "Uji Nonaktif",
                              "is_active": False})

    assert created["is_active"] is False
    assert all(row["code"] != "uji_nonaktif" for row in service.get_by_category("finance_category"))
