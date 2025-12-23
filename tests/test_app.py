import pytest
import os
from app import create_app

@pytest.fixture
def app():
    # Set minimal env vars for testing
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['JWT_SECRET_KEY'] = 'test_key'
    os.environ['SECRET_KEY'] = 'test_secret'
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['FLASK_DEBUG'] = '1'
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirect to login