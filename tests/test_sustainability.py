"""
Unit tests untuk memastikan sustainability aplikasi
Jalankan dengan: python -m pytest tests/ -v
"""

import pytest
import json
from app import create_app
from app.core.database import SessionLocal, engine, Base
import tempfile
import os

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    # Create temporary database for testing
    db_fd, db_path = tempfile.mkstemp()

    # Configure test database
    test_config = {
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{db_path}'
    }

    app = create_app()
    app.config.update(test_config)

    # Create tables
    with app.app_context():
        Base.metadata.create_all(bind=engine)

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    with app.app_context():
        session = SessionLocal()
        yield session
        session.rollback()
        session.close()

class TestHealthCheck:
    """Test health check endpoints"""

    def test_health_endpoint(self, client):
        """Test basic health check"""
        response = client.get('/health/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] in ['healthy', 'warning']
        assert 'services' in data
        assert 'database' in data['services']

    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get('/health/metrics')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'metrics' in data
        assert 'total_teachers' in data['metrics']

class TestPagination:
    """Test pagination functionality"""

    def test_pagination_parameters(self, client):
        """Test pagination parameter validation"""
        # Valid parameters
        response = client.get('/teacher/get_all?page=1&per_page=10')
        assert response.status_code in [200, 404]  # 404 if no data

        # Invalid page
        response = client.get('/teacher/get_all?page=0&per_page=10')
        assert response.status_code == 400

        # Invalid per_page
        response = client.get('/teacher/get_all?page=1&per_page=150')
        assert response.status_code == 400

class TestErrorHandling:
    """Test global error handling"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['error'] == 'Not Found'
        assert data['status_code'] == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed"""
        response = client.post('/health/health')  # GET only endpoint
        assert response.status_code == 405

class TestSecurityHeaders:
    """Test security headers"""

    def test_security_headers_present(self, client):
        """Test that security headers are added to responses"""
        response = client.get('/health/health')

        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'X-API-Version' in response.headers

class TestDatabaseConnection:
    """Test database connectivity"""

    def test_database_connection(self, db_session):
        """Test database connection and basic query"""
        from sqlalchemy import text
        # This should not raise an exception
        result = db_session.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

if __name__ == '__main__':
    pytest.main([__file__, '-v'])