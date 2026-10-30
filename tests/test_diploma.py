import datetime as dt

import pytest
from app import create_app
from app.core.database import SessionLocal
from app.models.diploma import Diploma
from app.models.log import Log

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    yield app.test_client()
    db = SessionLocal()
    for model in (Log, Diploma):
        db.query(model).delete()
    db.commit()
    db.close()

def _find_diploma(number):
    db = SessionLocal()
    try:
        return db.query(Diploma).filter_by(number=number).one()
    finally:
        db.close()

def _form(**overrides):
    # Nilai dikirim sebagai teks, sama seperti FormData dari halaman Data Ijazah
    form = {"number": "DN-FORM", "student_name": "Siswa Uji", "major": "Kimia Industri",
            "academic_year": "2025/2026", "is_collected": "true", "collected_at": "2026-07-01"}
    form.update(overrides)
    return form

def test_create_collected_saves_form_date(client, auth_header):
    response = client.post("/diploma/create", headers=auth_header(client.application), data=_form())

    assert response.status_code == 201
    diploma = _find_diploma("DN-FORM")
    assert diploma.is_collected is True
    assert diploma.collected_at == dt.datetime(2026, 7, 1)

def test_update_saves_form_date(client, auth_header):
    headers = auth_header(client.application)
    client.post("/diploma/create", headers=headers, data=_form())
    diploma_id = _find_diploma("DN-FORM").id

    response = client.post("/diploma/update", headers=headers,
                           data={"id": str(diploma_id), "is_collected": "true", "collected_at": "2026-08-02"})

    assert response.status_code == 200
    assert _find_diploma("DN-FORM").collected_at == dt.datetime(2026, 8, 2)

def test_create_rejects_invalid_date(client, auth_header):
    response = client.post("/diploma/create", headers=auth_header(client.application),
                           data=_form(collected_at="1 Juli 2026"))

    assert response.status_code == 400
    assert "Tanggal Pengambilan harus berformat YYYY-MM-DD" in response.get_json()["error"]
