import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from app import create_app
from app.core.database import SessionLocal
from app.models.master_reference import MasterReference
from app.models.teacher import Teacher
from migrate_teacher_codes import find_code, migrate

EMP_STATUS = {"PNS": "Pegawai Negeri Sipil", "GTT": "Guru Tidak Tetap"}

@pytest.mark.parametrize("value, expected", [
    ("Pegawai Negeri Sipil", "PNS"),
    ("pegawai negeri sipil", "PNS"),
    ("PNS", "PNS"),
    ("Honorer", None),
    (None, None),
])
def test_find_code(value, expected):
    assert find_code(value, EMP_STATUS) == expected

@pytest.fixture
def db():
    create_app()
    session = SessionLocal()
    session.add_all([
        MasterReference(category="teacher_emp_status", code="PNS", name="Pegawai Negeri Sipil"),
        MasterReference(category="teacher_active_status", code="aktif", name="Aktif"),
        MasterReference(category="teacher_rank", code="III/a", name="Penata Muda"),
    ])
    session.commit()
    yield session
    for model in (Teacher, MasterReference):
        session.query(model).delete()
    session.commit()
    session.close()

def _teacher(db, identity_number, **values):
    teacher = Teacher(identity_number=identity_number, full_name="Guru", gender="L", **values)
    db.add(teacher)
    db.commit()
    return teacher

def test_migrate_converts_names_and_keeps_codes(db):
    _teacher(db, "2001", employment_status="Pegawai Negeri Sipil", status="Aktif", rank="Penata Muda")
    _teacher(db, "2002", employment_status="PNS", status="aktif", rank="III/a")
    _teacher(db, "2003", employment_status="Honorer", status="Aktif")

    assert migrate(db, dry_run=False) == (2, 1)

    converted = db.query(Teacher).filter_by(identity_number="2001").one()
    assert (converted.employment_status, converted.status, converted.rank) == ("PNS", "aktif", "III/a")
    unknown = db.query(Teacher).filter_by(identity_number="2003").one()
    assert (unknown.employment_status, unknown.status) == ("Honorer", "aktif")

def test_migrate_dry_run_saves_nothing(db):
    _teacher(db, "2004", employment_status="Pegawai Negeri Sipil", status="Aktif")

    assert migrate(db, dry_run=True) == (1, 0)

    db.expire_all()
    assert db.query(Teacher).filter_by(identity_number="2004").one().employment_status == "Pegawai Negeri Sipil"
