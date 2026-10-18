import datetime as dt

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app import create_app
from app.core.database import SessionLocal, engine
from app.models.incoming_letter import IncomingLetter
from app.models.storage_location import StorageLocation

@pytest.fixture
def db():
    create_app()
    session = SessionLocal()
    yield session
    session.rollback()
    session.query(StorageLocation).delete()
    session.commit()
    session.close()

def test_every_connection_enables_sqlite_pragmas():
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA foreign_keys")).scalar() == 1
        assert conn.execute(text("PRAGMA journal_mode")).scalar() == "wal"
        assert conn.execute(text("PRAGMA busy_timeout")).scalar() == 5000

def test_foreign_key_is_enforced(db):
    db.add(IncomingLetter(number="FK-1", letter_date=dt.datetime.now(), received_date=dt.datetime.now(),
                          sender="A", subject="x", classification_id=99999))
    with pytest.raises(IntegrityError, match="FOREIGN KEY constraint failed"):
        db.commit()

def test_timestamps_use_local_time(db):
    location = StorageLocation(name="Lemari Uji Waktu")
    db.add(location)
    db.commit()

    assert abs(location.created_at - dt.datetime.now()) < dt.timedelta(minutes=1)
    assert abs(location.updated_at - dt.datetime.now()) < dt.timedelta(minutes=1)
