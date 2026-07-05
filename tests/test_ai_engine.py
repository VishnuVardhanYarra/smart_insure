import sys
import os
# Add root path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine import generate_mock_recommendation, generate_insurance_recommendation

def test_mock_recommendation_structure():
    user_data = {
        'name': 'Bob Tester',
        'age': '45',
        'gender': 'Male',
        'annual_income': '60000',
        'dependents': '3',
        'health_conditions': 'Hypertension',
        'lifestyle_habits': 'Smokes 5 cigarettes a day, sedentary',
        'insurance_preferences': 'Health Insurance, Term Life Insurance'
    }
    
    result = generate_mock_recommendation(user_data)
    
    # Check schema presence
    assert 'risk_score' in result
    assert 'risk_factors' in result
    assert 'premium_estimates' in result
    assert 'recommended_plans' in result
    assert 'financial_insights' in result
    
    # Check data integrity
    assert isinstance(result['risk_score'], int)
    assert result['risk_score'] > 30 # Due to age, smoking, hypertension, sedentary lifestyle
    assert len(result['risk_factors']) > 0
    assert 'term_life' in result['premium_estimates']
    assert 'health_insurance' in result['premium_estimates']
    
    # Check plans match preferences
    plans = result['recommended_plans']
    categories = [p['category'] for p in plans]
    assert 'Health Insurance' in categories
    assert 'Term Life Insurance' in categories

def test_ai_engine_graceful_fallback():
    # If GEMINI_API_KEY is not set or invalid, it should fall back to mock without raising an exception
    user_data = {
        'name': 'Fallback Test',
        'age': '28',
        'gender': 'Female',
        'annual_income': '45000',
        'dependents': '0',
        'health_conditions': '',
        'lifestyle_habits': 'exercise regularly',
        'insurance_preferences': 'Health Insurance'
    }
    
    # Even if key is missing or invalid, generate_insurance_recommendation should return valid schema
    result = generate_insurance_recommendation(user_data)
    
    assert 'risk_score' in result
    assert 'risk_factors' in result
    assert 'premium_estimates' in result
    assert 'recommended_plans' in result
    assert 'financial_insights' in result
    assert isinstance(result['risk_score'], int)
    assert result['risk_score'] < 30 # healthy habits, young
