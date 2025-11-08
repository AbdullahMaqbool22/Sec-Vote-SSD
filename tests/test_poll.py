"""
Unit tests for Poll Service
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.poll.app import app, db, Poll, PollOption
from shared.auth_utils import generate_token


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


@pytest.fixture
def auth_token():
    """Generate test authentication token"""
    return generate_token(1, 'testuser')


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200


def test_create_poll(client, auth_token):
    """Test poll creation"""
    response = client.post('/polls',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Test Poll',
            'description': 'This is a test poll',
            'options': ['Option 1', 'Option 2', 'Option 3']
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['poll']['title'] == 'Test Poll'
    assert len(data['poll']['options']) == 3


def test_create_poll_insufficient_options(client, auth_token):
    """Test poll creation with too few options"""
    response = client.post('/polls',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Test Poll',
            'options': ['Only One Option']
        }
    )
    
    assert response.status_code == 400
    assert b'At least 2 options are required' in response.data


def test_get_polls(client, auth_token):
    """Test getting all polls"""
    # Create a poll first
    client.post('/polls',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Test Poll',
            'options': ['Option 1', 'Option 2']
        }
    )
    
    # Get polls
    response = client.get('/polls')
    assert response.status_code == 200
    data = response.get_json()
    assert 'polls' in data
    assert len(data['polls']) > 0


def test_get_poll_by_id(client, auth_token):
    """Test getting a specific poll"""
    # Create a poll
    create_response = client.post('/polls',
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'title': 'Test Poll',
            'options': ['Option 1', 'Option 2']
        }
    )
    
    poll_id = create_response.get_json()['poll']['id']
    
    # Get the poll
    response = client.get(f'/polls/{poll_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Poll'
