import datetime as dt

import pytest
from app import create_app
from app.core.database import SessionLocal
from app.models.classification import Classification
from app.models.log import Log
from app.models.outgoing_letter import OutgoingLetter

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    db = SessionLocal()
    db.add(Classification(name="Sekolah", code="421", retention_active_period=2,
                          retention_inactive_period=5, final_action="permanent"))
    db.commit()
    db.close()
    yield app.test_client()
    db = SessionLocal()
    for model in (Log, OutgoingLetter, Classification):
        db.query(model).delete()
    db.commit()
    db.close()

def _find_letter(number):
    db = SessionLocal()
    try:
        return db.query(OutgoingLetter).filter_by(number=number).one()
    finally:
        db.close()

def _form(**overrides):
    db = SessionLocal()
    try:
        classification_id = db.query(Classification).filter_by(code="421").one().id
    finally:
        db.close()
    # Nilai dikirim sebagai teks, sama seperti FormData dari halaman Surat Keluar
    form = {"number": "OUT-FORM", "destination": "Dinas", "subject": "Uji", "letter_date": "2026-10-20",
            "sent_date": "2026-10-21", "classification_id": str(classification_id), "is_decree": "false"}
    form.update(overrides)
    return form

def test_create_saves_form_dates(client, auth_header):
    response = client.post("/outgoing_letter/create", headers=auth_header(client.application), data=_form())

    assert response.status_code == 201
    letter = _find_letter("OUT-FORM")
    assert letter.letter_date == dt.datetime(2026, 10, 20)
    assert letter.sent_date == dt.datetime(2026, 10, 21)

def test_update_saves_form_date(client, auth_header):
    headers = auth_header(client.application)
    client.post("/outgoing_letter/create", headers=headers, data=_form())
    letter_id = _find_letter("OUT-FORM").id

    response = client.post("/outgoing_letter/update", headers=headers,
                           data={"id": str(letter_id), "sent_date": "2026-12-01"})

    assert response.status_code == 200
    assert _find_letter("OUT-FORM").sent_date == dt.datetime(2026, 12, 1)

def test_create_rejects_invalid_date(client, auth_header):
    response = client.post("/outgoing_letter/create", headers=auth_header(client.application),
                           data=_form(sent_date="21-10-2026"))

    assert response.status_code == 400
    assert "Tanggal Kirim harus berformat YYYY-MM-DD" in response.get_json()["error"]
