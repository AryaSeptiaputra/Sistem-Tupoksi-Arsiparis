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

def test_get_by_keys_paginates_from_json_body(client):
    response = client.post("/incoming_letter/get_by_keys",
                           json={"filters": {"sender": "Dinas"}, "page": 2, "per_page": 2})

    assert response.status_code == 200
    body = response.get_json()
    assert body["pagination"]["total"] == 3
    assert body["pagination"]["page"] == 2
    assert len(body["data"]) == 1
