import datetime as dt

import pytest
from app import create_app
from app.core.database import SessionLocal
from app.models.classification import Classification
from app.models.diploma import Diploma
from app.models.finance_archive import FinanceArchive
from app.models.incoming_letter import IncomingLetter
from app.services.disposal import execute_disposal, get_expired_archives

OLD = dt.datetime(2015, 1, 1)

@pytest.fixture
def db():
    create_app()
    session = SessionLocal()
    yield session
    for model in (IncomingLetter, FinanceArchive, Diploma, Classification):
        session.query(model).delete()
    session.commit()
    session.close()

@pytest.fixture
def classifications(db):
    destroy = Classification(name="Umum", code="000", retention_active_period=1,
                             retention_inactive_period=1, final_action="destroy")
    permanent = Classification(name="Permanen", code="001", retention_active_period=1,
                               retention_inactive_period=1, final_action="permanent")
    db.add_all([destroy, permanent])
    db.commit()
    return destroy, permanent

def test_expired_archives_follow_retention_and_final_action(db, classifications):
    destroy, permanent = classifications
    db.add_all([
        IncomingLetter(number="IN-1", letter_date=OLD, received_date=OLD, sender="A", subject="", classification_id=destroy.id),
        IncomingLetter(number="IN-2", letter_date=dt.datetime.now(), received_date=OLD, sender="A", subject="Baru", classification_id=destroy.id),
        IncomingLetter(number="IN-3", letter_date=OLD, received_date=OLD, sender="A", subject="Permanen", classification_id=permanent.id),
        FinanceArchive(title="BOS", fiscal_year=2015, amount=1500000, classification_id=destroy.id),
        Diploma(number="D-1", student_name="Siswa", major="TKJ", academic_year="2015/2016", is_collected=True),
    ])
    db.commit()

    items = {item["number"] if item["number"] != "-" else item["title"]: item for item in get_expired_archives(db)}

    assert set(items) == {"IN-1", "BOS (Rp 1,500,000)", "D-1"}
    assert items["IN-1"]["title"] == "(Tanpa Perihal)"
    assert items["IN-1"]["expiry_year"] == 2017
    assert items["D-1"]["expiry_year"] == 2020

def test_execute_disposal_marks_destroyed(db, classifications):
    destroy, _ = classifications
    letter = IncomingLetter(number="IN-1", letter_date=OLD, received_date=OLD, sender="A", subject="x", classification_id=destroy.id)
    db.add(letter)
    db.commit()

    count = execute_disposal(db, [{"table_source": "incoming_letter", "id": letter.id},
                                  {"table_source": "tidak_ada", "id": 1}], None)

    assert count == 1
    assert db.get(IncomingLetter, letter.id).archive_status == "destroyed"
    assert get_expired_archives(db) == []
