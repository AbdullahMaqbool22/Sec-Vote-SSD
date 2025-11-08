"""
Unit tests for Authentication Service
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.auth.app import app, db, User


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert b'healthy' in response.data


def test_register_user(client):
    """Test user registration"""
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test1234'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully'
    assert 'token' in data
    assert data['user']['username'] == 'testuser'


def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    # Register first user
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test1@example.com',
        'password': 'Test1234'
    })
    
    # Try to register with same username
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test2@example.com',
        'password': 'Test1234'
    })
    
    assert response.status_code == 409
    assert b'Username already exists' in response.data


def test_register_invalid_email(client):
    """Test registration with invalid email"""
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'invalid-email',
        'password': 'Test1234'
    })
    
    assert response.status_code == 400
    assert b'Invalid email format' in response.data


def test_register_weak_password(client):
    """Test registration with weak password"""
    response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'weak'
    })
    
    assert response.status_code == 400
    assert b'Password must be at least 8 characters' in response.data


def test_login_success(client):
    """Test successful login"""
    # Register user first
    client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test1234'
    })
    
    # Login
    response = client.post('/login', json={
        'username': 'testuser',
        'password': 'Test1234'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Login successful'
    assert 'token' in data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/login', json={
        'username': 'nonexistent',
        'password': 'WrongPass123'
    })
    
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data


def test_verify_token(client):
    """Test token verification"""
    # Register and get token
    register_response = client.post('/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test1234'
    })
    
    token = register_response.get_json()['token']
    
    # Verify token
    response = client.post('/verify', json={'token': token})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] is True
    assert data['username'] == 'testuser'
