import pytest
from app import create_app

# Endpoint data yang wajib login: (method, path)
PROTECTED_ENDPOINTS = [
    ("GET", "/teacher/get_all"),
    ("POST", "/teacher/get_by_keys"),
    ("GET", "/classification/get_all"),
    ("POST", "/classification/get_by_keys"),
    ("GET", "/incoming_letter/get_all"),
    ("POST", "/incoming_letter/get_by_keys"),
    ("GET", "/outgoing_letter/get_all"),
    ("POST", "/outgoing_letter/get_by_keys"),
    ("GET", "/diploma/get_all"),
    ("POST", "/diploma/get_by_keys"),
    ("GET", "/finance_archive/get_all"),
    ("GET", "/employee_archive/get_all"),
    ("GET", "/storage_location/get_all"),
    ("GET", "/log/get_all"),
    ("GET", "/api/references/archive_status"),
    ("POST", "/api/references"),
    ("PUT", "/api/references/1"),
    ("DELETE", "/api/references/1"),
    ("GET", "/user/me"),
    ("GET", "/disposal/check"),
    ("GET", "/backup/logs"),
]

@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

@pytest.mark.parametrize("method, path", PROTECTED_ENDPOINTS)
def test_rejects_request_without_token(client, method, path):
    response = client.open(path, method=method, json={})

    assert response.status_code == 401

@pytest.mark.parametrize("method, path", PROTECTED_ENDPOINTS)
def test_rejects_invalid_token_with_401(client, method, path):
    response = client.open(path, method=method, json={},
                           headers={"Authorization": "Bearer token.tidak.valid"})

    assert response.status_code == 401
