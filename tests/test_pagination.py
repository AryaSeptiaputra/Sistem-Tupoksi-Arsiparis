"""
Test cases untuk backend optimization.
Gunakan pytest untuk menjalankan tests.

Setup:
  pip install pytest pytest-flask

Run:
  pytest tests/test_pagination.py -v
"""

import pytest
from flask import request
from app import create_app
from app.core.database import SessionLocal, Base, engine
from app.models.incoming_letter import IncomingLetter
from app.utils.pagination import PaginationParams, paginate_query, get_pagination_params
from app.utils.response import success_response, error_response
import datetime


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    
    # Create tables
    with app.app_context():
        Base.metadata.create_all(bind=engine)
        yield app
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """Create sample incoming letters for testing"""
    session = SessionLocal()
    
    try:
        # Create 150 sample records
        for i in range(150):
            letter = IncomingLetter(
                number=f"LETTER-{i+1:04d}",
                letter_date=datetime.datetime.now(),
                received_date=datetime.datetime.now(),
                sender=f"Sender {i % 5 + 1}",
                subject=f"Subject {i}",
                attachment_path=None,
                classification_id=1,
                storage_location_id=None,
                archive_status='active',
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            session.add(letter)
        
        session.commit()
        yield session
    finally:
        session.close()


# =============================================================================
# Test Pagination Params
# =============================================================================

def test_pagination_params_default():
    """Test default pagination parameters"""
    params = PaginationParams()
    
    assert params.page == 1
    assert params.per_page == 20
    assert params.sort_by == 'id'
    assert params.sort_order == 'asc'
    assert params.offset == 0


def test_pagination_params_custom():
    """Test custom pagination parameters"""
    params = PaginationParams(page=3, per_page=50, sort_by='number', sort_order='desc')
    
    assert params.page == 3
    assert params.per_page == 50
    assert params.sort_by == 'number'
    assert params.sort_order == 'desc'
    assert params.offset == 100  # (3-1) * 50


def test_pagination_params_max_per_page():
    """Test max per_page limit (100)"""
    params = PaginationParams(per_page=999)
    
    assert params.per_page == 100  # Should be capped at 100


def test_pagination_params_min_page():
    """Test minimum page validation"""
    params = PaginationParams(page=0)
    
    assert params.page == 1  # Should default to 1


def test_pagination_params_invalid_sort_order():
    """Test invalid sort order"""
    params = PaginationParams(sort_order='invalid')
    
    assert params.sort_order == 'asc'  # Should default to 'asc'


def test_pagination_params_to_dict():
    """Test to_dict() method"""
    params = PaginationParams(page=2, per_page=25)
    result = params.to_dict()
    
    assert result['page'] == 2
    assert result['per_page'] == 25
    assert result['sort_by'] == 'id'
    assert result['sort_order'] == 'asc'


# =============================================================================
# Test Paginate Query
# =============================================================================

def test_paginate_query_first_page(app, sample_data):
    """Test pagination for first page"""
    params = PaginationParams(page=1, per_page=50)
    query = SessionLocal().query(IncomingLetter)
    result = paginate_query(query, params)
    
    assert len(result.items) == 50
    assert result.page == 1
    assert result.total == 150
    assert result.total_pages == 3
    assert result.has_next is True
    assert result.has_prev is False


def test_paginate_query_last_page(app, sample_data):
    """Test pagination for last page"""
    params = PaginationParams(page=3, per_page=50)
    query = SessionLocal().query(IncomingLetter)
    result = paginate_query(query, params)
    
    assert len(result.items) == 50
    assert result.page == 3
    assert result.total == 150
    assert result.total_pages == 3
    assert result.has_next is False
    assert result.has_prev is True


def test_paginate_query_middle_page(app, sample_data):
    """Test pagination for middle page"""
    params = PaginationParams(page=2, per_page=50)
    query = SessionLocal().query(IncomingLetter)
    result = paginate_query(query, params)
    
    assert len(result.items) == 50
    assert result.page == 2
    assert result.has_next is True
    assert result.has_prev is True


def test_paginate_query_to_dict(app, sample_data):
    """Test PaginatedResult.to_dict()"""
    params = PaginationParams(page=1, per_page=50)
    query = SessionLocal().query(IncomingLetter)
    result = paginate_query(query, params)
    result.items = [{'id': 1}]  # Mock data
    
    result_dict = result.to_dict()
    
    assert 'data' in result_dict
    assert 'pagination' in result_dict
    assert result_dict['pagination']['page'] == 1
    assert result_dict['pagination']['total'] == 150
    assert result_dict['pagination']['has_next'] is True


# =============================================================================
# Test Response Formatting
# =============================================================================

def test_success_response():
    """Test success response format"""
    data = {'id': 1, 'name': 'Test'}
    response, status_code = success_response(data, "Success", 200)
    
    json_response = response.get_json()
    
    assert json_response['success'] is True
    assert json_response['message'] == 'Success'
    assert json_response['data'] == data
    assert status_code == 200


def test_error_response():
    """Test error response format"""
    response, status_code = error_response("Not found", 404)
    
    json_response = response.get_json()
    
    assert json_response['success'] is False
    assert json_response['message'] == 'Not found'
    assert status_code == 404


def test_error_response_with_details():
    """Test error response with additional details"""
    errors = {'field': ['Error message']}
    response, status_code = error_response("Validation failed", 422, errors)
    
    json_response = response.get_json()
    
    assert json_response['success'] is False
    assert json_response['errors'] == errors
    assert status_code == 422


# =============================================================================
# Test Get Pagination Params from Request
# =============================================================================

def test_get_pagination_params_from_request(app):
    """Test extracting pagination params from request"""
    with app.test_request_context('/?page=2&per_page=25&sort_order=desc'):
        params = get_pagination_params(request.args)
        
        assert params.page == 2
        assert params.per_page == 25
        assert params.sort_order == 'desc'


def test_get_pagination_params_defaults(app):
    """Test default pagination params from request"""
    with app.test_request_context('/'):
        params = get_pagination_params(request.args)
        
        assert params.page == 1
        assert params.per_page == 20
        assert params.sort_by == 'id'
        assert params.sort_order == 'asc'


# =============================================================================
# Integration Tests with API Endpoints
# =============================================================================

def test_get_all_endpoint_with_pagination(client, sample_data):
    """Test /incoming_letter/get_all with pagination"""
    # Need to authenticate first - this is simplified
    # In real tests, mock JWT token
    
    response = client.get('/incoming_letter/get_all?page=1&per_page=50')
    # If auth is required, status will be 401
    # Assume auth is mocked or disabled for testing


def test_get_all_endpoint_default_page(client, sample_data):
    """Test /incoming_letter/get_all defaults to page 1"""
    # Default should return page 1 with 20 items per page
    pass


def test_get_by_keys_with_filter(client):
    """Test /incoming_letter/get_by_keys with filters"""
    payload = {
        "filters": {
            "sender": "John",
            "archive_status": "active"
        },
        "page": 1,
        "per_page": 20
    }
    
    response = client.post(
        '/incoming_letter/get_by_keys',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    # Check response format and status


# =============================================================================
# Performance Tests
# =============================================================================

def test_pagination_large_dataset(app):
    """Test pagination performance with large dataset"""
    import time
    
    session = SessionLocal()
    
    try:
        # Create 1000 records
        print("\nCreating 1000 test records...")
        for i in range(1000):
            letter = IncomingLetter(
                number=f"PERF-{i+1:06d}",
                letter_date=datetime.datetime.now(),
                received_date=datetime.datetime.now(),
                sender=f"Sender {i % 10}",
                subject=f"Subject {i}",
                classification_id=1,
                archive_status='active',
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now()
            )
            session.add(letter)
            if (i + 1) % 100 == 0:
                session.commit()
                print(f"  Created {i+1} records...")
        
        session.commit()
        
        # Test pagination performance
        params = PaginationParams(page=1, per_page=50)
        query = session.query(IncomingLetter)
        
        start_time = time.time()
        result = paginate_query(query, params)
        elapsed = time.time() - start_time
        
        print(f"\nPagination performance:")
        print(f"  Retrieved {len(result.items)} items")
        print(f"  Time: {elapsed:.3f} seconds")
        print(f"  Total records: {result.total}")
        
        # Should be very fast (< 100ms for first page)
        assert elapsed < 0.1, f"Pagination took too long: {elapsed}s"
        
    finally:
        session.close()


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
