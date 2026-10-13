import pytest
import sys
import os

# Add root path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retirement_engine import calculate_retirement_gap, simulate_what_if, format_inr
from app import app, db
from models import User, RetirementPlan

def test_format_inr():
    assert format_inr(15000000) == "₹1.50 Cr"
    assert format_inr(450000) == "₹4.50 L"
    assert format_inr(25000) == "₹25,000"
    assert format_inr(0) == "₹0"
    assert format_inr(-2500000) == "-₹25.00 L"

def test_calculate_retirement_gap_standard():
    params = {
        'current_age': 30,
        'retirement_age': 60,
        'current_savings': 1000000,
        'monthly_expenses': 50000,
        'monthly_savings': 20000,
        'expected_retirement_income': 0,
        'annual_insurance_budget': 25000,
        'inflation_rate': 6.0,
        'pre_retire_roi': 10.0,
        'post_retire_roi': 7.0,
        'life_expectancy': 85
    }
    result = calculate_retirement_gap(params)
    assert result['success'] is True
    assert result['years_to_retire'] == 30
    assert result['years_in_retire'] == 25
    
    # 50,000 * (1.06)^30 approx 287,174
    assert result['projected_monthly_expense'] > 250000
    assert result['required_corpus'] > 50000000 # More than 5 Cr
    assert result['total_available_corpus'] > 40000000 # Compounded current + SIP
    assert result['financial_gap'] > 0 # Expect shortfall
    assert result['readiness_percentage'] > 50
    assert result['readiness_percentage'] < 100
    assert result['status'] in ['moderate_gap', 'significant_gap']
    assert result['additional_monthly_savings'] > 0
    assert len(result['recommendations']) > 0

def test_calculate_retirement_gap_surplus():
    # Wealthy individual with huge savings and high SIP
    params = {
        'current_age': 40,
        'retirement_age': 55,
        'current_savings': 50000000, # 5 Cr
        'monthly_expenses': 60000,
        'monthly_savings': 100000,
        'expected_retirement_income': 50000,
        'inflation_rate': 6.0,
        'pre_retire_roi': 10.0,
        'post_retire_roi': 7.0
    }
    result = calculate_retirement_gap(params)
    assert result['success'] is True
    assert result['status'] == 'surplus'
    assert result['financial_gap'] < 0 # Negative gap means surplus
    assert result['readiness_percentage'] >= 100
    assert result['additional_monthly_savings'] == 0.0
    assert "surplus" in result['recommendations'][0].lower()

def test_what_if_early_retirement_simulation():
    # What happens if user retires at 55 instead of 60?
    baseline = {
        'current_age': 30,
        'retirement_age': 60,
        'current_savings': 1000000,
        'monthly_expenses': 50000,
        'monthly_savings': 20000
    }
    scenario = {
        'current_age': 30,
        'retirement_age': 55, # 5 years earlier
        'current_savings': 1000000,
        'monthly_expenses': 50000,
        'monthly_savings': 20000
    }
    
    sim = simulate_what_if(baseline, scenario)
    assert sim['success'] is True
    deltas = sim['deltas']
    assert deltas['delta_retire_age'] == -5
    # Retiring earlier cuts accumulation compounding and increases living years
    assert deltas['delta_available_corpus'] < 0
    assert deltas['delta_gap'] > 0 # Gap widens significantly
    assert deltas['delta_readiness'] < 0 # Readiness score drops
    
    # Verify insightful explanation generated
    insights = sim['actuarial_insights']
    assert len(insights) > 0
    assert any("earlier" in text.lower() for text in insights)

def test_what_if_increased_savings_simulation():
    # What happens if user increases SIP from 20k to 35k?
    baseline = {
        'current_age': 30,
        'retirement_age': 60,
        'current_savings': 1000000,
        'monthly_expenses': 50000,
        'monthly_savings': 20000
    }
    scenario = {
        'current_age': 30,
        'retirement_age': 60,
        'current_savings': 1000000,
        'monthly_expenses': 50000,
        'monthly_savings': 35000 # +15k/mo
    }
    
    sim = simulate_what_if(baseline, scenario)
    assert sim['success'] is True
    deltas = sim['deltas']
    assert deltas['delta_monthly_savings'] == 15000
    assert deltas['delta_available_corpus'] > 0
    assert deltas['delta_gap'] < 0 # Gap shrinks
    assert deltas['delta_readiness'] > 0 # Readiness improves

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_retirement_page_route(client):
    response = client.get('/retirement')
    assert response.status_code == 200
    assert b"Retirement Readiness" in response.data
    assert b"What-If" in response.data

def test_api_retirement_calculate_endpoint(client):
    payload = {
        'current_age': 32,
        'retirement_age': 58,
        'current_savings': 800000,
        'monthly_expenses': 45000,
        'monthly_savings': 18000
    }
    response = client.post('/api/retirement/calculate', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'required_corpus' in data
    assert 'total_available_corpus' in data
    assert 'financial_gap' in data
    assert 'readiness_percentage' in data

def test_api_retirement_simulate_endpoint(client):
    payload = {
        'baseline': {
            'current_age': 30,
            'retirement_age': 60,
            'monthly_savings': 15000,
            'monthly_expenses': 40000
        },
        'scenario': {
            'current_age': 30,
            'retirement_age': 55,
            'monthly_savings': 25000,
            'monthly_expenses': 35000
        }
    }
    response = client.post('/api/retirement/simulate', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'baseline' in data
    assert 'scenario' in data
    assert 'deltas' in data
    assert 'actuarial_insights' in data
