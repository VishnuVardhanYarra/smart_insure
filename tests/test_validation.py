import sys
import os
# Add root path to sys.path to allow imports from app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import validate_user_input

def test_valid_user_input():
    valid_data = {
        'name': 'John Doe',
        'age': '35',
        'gender': 'Male',
        'annual_income': '75000',
        'dependents': '2'
    }
    errors = validate_user_input(valid_data)
    assert len(errors) == 0

def test_invalid_name():
    # Empty name
    data_empty = {'name': '', 'age': '35', 'gender': 'Male', 'annual_income': '75000', 'dependents': '2'}
    errors = validate_user_input(data_empty)
    assert "Name is required." in errors

    # Short name
    data_short = {'name': 'J', 'age': '35', 'gender': 'Male', 'annual_income': '75000', 'dependents': '2'}
    errors = validate_user_input(data_short)
    assert "Name must be at least 2 characters." in errors

def test_invalid_age():
    # Age too low
    data_young = {'name': 'John Doe', 'age': '17', 'gender': 'Male', 'annual_income': '75000', 'dependents': '2'}
    errors = validate_user_input(data_young)
    assert "Age must be between 18 and 100." in errors

    # Age too high
    data_old = {'name': 'John Doe', 'age': '101', 'gender': 'Male', 'annual_income': '75000', 'dependents': '2'}
    errors = validate_user_input(data_old)
    assert "Age must be between 18 and 100." in errors

    # Age non-integer
    data_string = {'name': 'John Doe', 'age': 'thirty', 'gender': 'Male', 'annual_income': '75000', 'dependents': '2'}
    errors = validate_user_input(data_string)
    assert "Age must be a valid integer." in errors

def test_invalid_gender():
    data_gender = {'name': 'John Doe', 'age': '35', 'gender': 'Alien', 'annual_income': '75000', 'dependents': '2'}
    errors = validate_user_input(data_gender)
    assert "Please select a valid gender option." in errors

def test_invalid_income():
    # Negative income
    data_neg = {'name': 'John Doe', 'age': '35', 'gender': 'Male', 'annual_income': '-100', 'dependents': '2'}
    errors = validate_user_input(data_neg)
    assert "Annual income cannot be negative." in errors

    # Non-numeric income
    data_string = {'name': 'John Doe', 'age': '35', 'gender': 'Male', 'annual_income': 'abc', 'dependents': '2'}
    errors = validate_user_input(data_string)
    assert "Annual income must be a valid number." in errors

def test_invalid_dependents():
    # Negative dependents
    data_neg = {'name': 'John Doe', 'age': '35', 'gender': 'Male', 'annual_income': '75000', 'dependents': '-1'}
    errors = validate_user_input(data_neg)
    assert "Dependents must be between 0 and 20." in errors

    # Too many dependents
    data_many = {'name': 'John Doe', 'age': '35', 'gender': 'Male', 'annual_income': '75000', 'dependents': '21'}
    errors = validate_user_input(data_many)
    assert "Dependents must be between 0 and 20." in errors

    # Non-numeric dependents
    data_string = {'name': 'John Doe', 'age': '35', 'gender': 'Male', 'annual_income': '75000', 'dependents': 'two'}
    errors = validate_user_input(data_string)
    assert "Number of dependents must be a valid integer." in errors
