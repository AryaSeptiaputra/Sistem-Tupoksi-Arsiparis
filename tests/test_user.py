import pytest
from app import create_app
from app.core.database import SessionLocal
from app.models.log import Log
from app.models.user import User
from app.services.auth import login_user
from app.services.user import (
    create_user, update_profile, change_password, reset_password
)

PASSWORD = "Rahasia123"

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app
    db = SessionLocal()
    db.query(Log).delete()
    db.query(User).delete()
    db.commit()
    db.close()

@pytest.fixture
def db(app):
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def operator(db):
    return create_user(db, "arsiparis", "Operator Arsip", PASSWORD)

def test_create_user_rejects_second_active_account(db, operator):
    with pytest.raises(ValueError, match="satu pengguna"):
        create_user(db, "lain", "Akun Lain", PASSWORD)

def test_create_user_rejects_weak_password(db):
    with pytest.raises(ValueError):
        create_user(db, "arsiparis", "Operator Arsip", "lemah")

def test_login_user_checks_password_and_active_flag(db, operator):
    assert login_user(db, "arsiparis", PASSWORD).id == operator.id
    assert login_user(db, "arsiparis", "Salah1234") is None
    assert login_user(db, "tidakada", PASSWORD) is None

    operator.is_active = False
    db.commit()
    assert login_user(db, "arsiparis", PASSWORD) is None

def test_update_profile_changes_username(db, operator):
    updated = update_profile(db, operator.id, "operator2", "Nama Baru")
    assert updated.username == "operator2"
    assert updated.display_name == "Nama Baru"

def test_update_profile_rejects_empty_name(db, operator):
    with pytest.raises(ValueError):
        update_profile(db, operator.id, "arsiparis", "  ")

def test_change_password_requires_old_password(db, operator):
    with pytest.raises(ValueError, match="lama salah"):
        change_password(db, operator.id, "Salah1234", "BaruSekali1")

    change_password(db, operator.id, PASSWORD, "BaruSekali1")
    assert login_user(db, "arsiparis", "BaruSekali1") is not None

def test_reset_password_without_old_password(db, operator):
    reset_password(db, "arsiparis", "Reset12345")
    assert login_user(db, "arsiparis", "Reset12345") is not None

def test_log_without_user_is_system(db):
    log = Log(action="Backup terjadwal", user_id=None)
    db.add(log)
    db.commit()
    assert log.to_dict()["username"] == "Sistem"

def test_login_route_and_account_endpoints(app, operator):
    client = app.test_client()

    bad = client.post("/auth/login", json={"username": "arsiparis", "password": "Salah1234"})
    assert bad.status_code == 401

    ok = client.post("/auth/login", json={"username": "arsiparis", "password": PASSWORD})
    assert ok.status_code == 200
    headers = {"Authorization": f"Bearer {ok.get_json()['access_token']}"}

    me = client.get("/user/me", headers=headers).get_json()
    assert me["username"] == "arsiparis"
    assert me["last_login_at"] is not None
    assert "role" not in me

    changed = client.post("/user/change_password", headers=headers,
                          json={"old_password": PASSWORD, "new_password": "BaruSekali1"})
    assert changed.status_code == 200

def test_account_endpoints_require_login(app):
    client = app.test_client()
    assert client.get("/user/me").status_code == 401
    assert client.get("/user/get_all").status_code == 404
