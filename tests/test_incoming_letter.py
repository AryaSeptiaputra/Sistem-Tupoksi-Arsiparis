import datetime as dt

import pytest
from app import create_app
from app.core.database import SessionLocal
from app.models.classification import Classification
from app.models.incoming_letter import IncomingLetter

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    db = SessionLocal()
    classification = Classification(name="Umum", code="000", retention_active_period=1,
                                    retention_inactive_period=1, final_action="destroy")
    db.add(classification)
    db.commit()
    db.add_all([
        IncomingLetter(number=f"IN-{i}", letter_date=dt.datetime(2024, 1, 1), received_date=dt.datetime(2024, 1, 1),
                       sender="Dinas" if i < 3 else "Lain", subject="x", classification_id=classification.id)
        for i in range(4)
    ])
    db.commit()
    yield app.test_client()
    db.query(IncomingLetter).delete()
    db.query(Classification).delete()
    db.commit()
    db.close()

def test_get_by_keys_paginates_from_json_body(client, auth_header):
    response = client.post("/incoming_letter/get_by_keys", headers=auth_header(client.application),
                           json={"filters": {"sender": "Dinas"}, "page": 2, "per_page": 2})

    assert response.status_code == 200
    body = response.get_json()
    assert body["pagination"]["total"] == 3
    assert body["pagination"]["page"] == 2
    assert len(body["data"]) == 1

def _find_letter(number):
    db = SessionLocal()
    try:
        return db.query(IncomingLetter).filter_by(number=number).one()
    finally:
        db.close()

def _form(**overrides):
    db = SessionLocal()
    try:
        classification_id = db.query(Classification).filter_by(code="000").one().id
    finally:
        db.close()
    # Nilai dikirim sebagai teks, sama seperti FormData dari halaman Surat Masuk
    form = {"number": "IN-FORM", "sender": "Dinas", "subject": "Uji", "letter_date": "2026-10-20",
            "received_date": "2026-10-21", "classification_id": str(classification_id)}
    form.update(overrides)
    return form

def test_create_saves_form_dates(client, auth_header):
    response = client.post("/incoming_letter/create", headers=auth_header(client.application), data=_form())

    assert response.status_code == 201
    letter = _find_letter("IN-FORM")
    assert letter.letter_date == dt.datetime(2026, 10, 20)
    assert letter.received_date == dt.datetime(2026, 10, 21)

def test_update_saves_form_date(client, auth_header):
    letter_id = _find_letter("IN-0").id
    response = client.post("/incoming_letter/update", headers=auth_header(client.application),
                           data={"id": str(letter_id), "letter_date": "2026-11-05"})

    assert response.status_code == 200
    assert _find_letter("IN-0").letter_date == dt.datetime(2026, 11, 5)

def test_create_rejects_invalid_date(client, auth_header):
    response = client.post("/incoming_letter/create", headers=auth_header(client.application),
                           data=_form(letter_date="20/10/2026"))

    assert response.status_code == 400
    assert "Tanggal Surat harus berformat YYYY-MM-DD" in response.get_json()["message"]
