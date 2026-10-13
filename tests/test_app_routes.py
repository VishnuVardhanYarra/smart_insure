import sys
import os
import pytest

# Add root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import UserRecommendation

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory db for clean tests
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'insuresmart'

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"InsureSmart" in response.data
    assert b"Start Free Risk Analysis" in response.data

def test_assess_page_get(client):
    response = client.get('/assess')
    assert response.status_code == 200
    assert b"Demographics" in response.data
    assert b"Full Name" in response.data

def test_assess_submit_valid(client):
    # Post a valid form submission
    post_data = {
        'name': 'Test Client',
        'age': '40',
        'gender': 'Female',
        'annual_income': '80000',
        'dependents': '1',
        'health_conditions': 'None',
        'lifestyle_habits': 'Runs twice a week',
        'preferences': ['Health Insurance', 'Term Life Insurance']
    }
    
    # Flask redirects to dashboard upon success
    response = client.post('/assess', data=post_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Report Preview" not in response.data # Make sure it's the actual dashboard, not mockup
    assert b"Test Client" in response.data
    assert b"Risk Index" in response.data
    assert b"AI Financial Protection Insights" in response.data
    
    # Verify it was added to database
    with app.app_context():
        records = UserRecommendation.query.all()
        assert len(records) == 1
        assert records[0].name == 'Test Client'
        assert records[0].age == 40
        assert records[0].risk_score is not None

def test_assess_submit_invalid(client):
    # Send post with invalid age
    post_data = {
        'name': 'Young User',
        'age': '15', # Min age is 18
        'gender': 'Male',
        'annual_income': '20000',
        'dependents': '0',
        'health_conditions': '',
        'lifestyle_habits': '',
        'preferences': ['Health Insurance']
    }
    
    # Should not redirect, should render the form again with error flashed
    response = client.post('/assess', data=post_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Age must be between 18 and 100." in response.data
    
    # Verify database is empty
    with app.app_context():
        records = UserRecommendation.query.all()
        assert len(records) == 0

def test_history_hub_view(client):
    # Add a dummy record first
    with app.app_context():
        rec = UserRecommendation(
            name='Alice Wonderland',
            age=25,
            gender='Female',
            annual_income=90000,
            dependents=0,
            health_conditions='None',
            lifestyle_habits='None',
            insurance_preferences='Health Insurance',
            risk_score=20,
            risk_factors=['Healthy young age.'],
            premium_estimates={'health_insurance': {'base_premium': '$90/month', 'factors': 'Low risk'}},
            recommended_plans=[{'category': 'Health', 'plan_name': 'SmartShield', 'coverage': '$100,000', 'estimated_premium': '$90/month', 'why_recommended': 'Fit profile', 'priority': 'Medium'}],
            financial_insights={'savings_opportunity': 'Exercise'}
        )
        db.session.add(rec)
        db.session.commit()
        
    response = client.get('/history')
    assert response.status_code == 200
    assert b"Alice Wonderland" in response.data
    assert b"25 / Female" in response.data
    
    # Test search function
    response_search_found = client.get('/history?search=Alice')
    assert b"Alice Wonderland" in response_search_found.data
    
    response_search_not_found = client.get('/history?search=Bob')
    assert b"Alice Wonderland" not in response_search_not_found.data
    assert b"No Records Match Your Search" in response_search_not_found.data
