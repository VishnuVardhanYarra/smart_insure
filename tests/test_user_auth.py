import sys
import os
import pytest

# Add root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, UserRecommendation

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_registration(client):
    response = client.post('/register', data={
        'username': 'johndoe',
        'email': 'john@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Account created successfully" in response.data
    
    with app.app_context():
        user = User.query.filter_by(username='johndoe').first()
        assert user is not None
        assert user.email == 'john@example.com'

def test_user_login_logout(client):
    # Register first
    client.post('/register', data={
        'username': 'janedoe',
        'email': 'jane@example.com',
        'password': 'secretpassword'
    })
    
    # Logout
    client.get('/logout')
    
    # Login
    response = client.post('/login', data={
        'username': 'janedoe',
        'password': 'secretpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Welcome back, janedoe!" in response.data
    
    # Test Logout again
    response_logout = client.get('/logout', follow_redirects=True)
    assert b"You have been logged out." in response_logout.data


def test_user_history_isolation(client):
    # Register User A
    client.post('/register', data={'username': 'userA', 'email': 'usera@example.com', 'password': 'password123'})
    client.post('/assess', data={'name': 'User A Assessment', 'age': '30', 'gender': 'Male', 'annual_income': '50000', 'dependents': '1', 'preferences': ['Health Insurance']}, follow_redirects=True)
    
    # Verify User A sees their own record
    res_a = client.get('/history')
    assert b"User A Assessment" in res_a.data
    
    # Logout User A
    client.get('/logout')
    
    # Register User B
    client.post('/register', data={'username': 'userB', 'email': 'userb@example.com', 'password': 'password123'})
    client.post('/assess', data={'name': 'User B Assessment', 'age': '40', 'gender': 'Female', 'annual_income': '90000', 'dependents': '2', 'preferences': ['Term Life Insurance']}, follow_redirects=True)
    
    # Verify User B sees ONLY User B's record and NOT User A's record!
    res_b = client.get('/history')
    assert b"User B Assessment" in res_b.data
    assert b"User A Assessment" not in res_b.data
