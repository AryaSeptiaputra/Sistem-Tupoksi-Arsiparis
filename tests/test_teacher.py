import pytest
from app import create_app
from app.core.database import SessionLocal
from app.errors import DataInUseError
from app.models.employee_archive import EmployeeArchive
from app.models.teacher import Teacher
from app.services.teacher import delete_teacher

@pytest.fixture
def db():
    create_app()
    session = SessionLocal()
    yield session
    for model in (EmployeeArchive, Teacher):
        session.query(model).delete()
    session.commit()
    session.close()

def _teacher(db, identity_number):
    teacher = Teacher(identity_number=identity_number, full_name="Guru Uji", gender="L",
                      employment_status="GTT", status="aktif")
    db.add(teacher)
    db.commit()
    return teacher

def test_delete_teacher_without_archives(db):
    teacher = _teacher(db, "1001")

    assert delete_teacher(db, teacher.id) is not None
    assert db.query(Teacher).filter_by(identity_number="1001").first() is None

def test_delete_teacher_with_archives_is_rejected(db):
    teacher = _teacher(db, "1002")
    db.add(EmployeeArchive(document_name="SK Uji", document_type="SK_PANGKAT", owner_id=teacher.id))
    db.commit()

    with pytest.raises(DataInUseError, match="1 arsip pegawai"):
        delete_teacher(db, teacher.id)

    db.rollback()
    assert db.query(Teacher).filter_by(identity_number="1002").first() is not None
    assert db.query(EmployeeArchive).filter_by(document_name="SK Uji").first() is not None
