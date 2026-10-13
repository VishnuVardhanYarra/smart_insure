from datetime import datetime, timezone
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    recommendations = db.relationship('UserRecommendation', backref='user', lazy=True)
    retirement_plans = db.relationship('RetirementPlan', backref='user', lazy=True)

class UserRecommendation(db.Model):
    __tablename__ = 'user_recommendation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    dependents = db.Column(db.Integer, nullable=False)
    health_conditions = db.Column(db.Text, nullable=True) # Text list or comma-separated
    lifestyle_habits = db.Column(db.Text, nullable=True) # Text list (smoking, alcohol, exercise frequency, diet)
    insurance_preferences = db.Column(db.Text, nullable=True) # Comma-separated categories (e.g. Life, Health)

    # AI Recommendation Outlines (stored as JSON structures in SQLite Text columns)
    risk_score = db.Column(db.Integer, nullable=True)
    risk_factors_raw = db.Column(db.Text, nullable=True) # JSON Array of strings
    premium_estimates_raw = db.Column(db.Text, nullable=True) # JSON Object
    recommended_plans_raw = db.Column(db.Text, nullable=True) # JSON Array of objects
    financial_insights_raw = db.Column(db.Text, nullable=True) # JSON Object

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Helper properties for JSON handling
    @property
    def risk_factors(self):
        try:
            return json.loads(self.risk_factors_raw) if self.risk_factors_raw else []
        except Exception:
            return []

    @risk_factors.setter
    def risk_factors(self, value):
        self.risk_factors_raw = json.dumps(value) if value else '[]'

    @property
    def premium_estimates(self):
        try:
            return json.loads(self.premium_estimates_raw) if self.premium_estimates_raw else {}
        except Exception:
            return {}

    @premium_estimates.setter
    def premium_estimates(self, value):
        self.premium_estimates_raw = json.dumps(value) if value else '{}'

    @property
    def recommended_plans(self):
        try:
            return json.loads(self.recommended_plans_raw) if self.recommended_plans_raw else []
        except Exception:
            return []

    @recommended_plans.setter
    def recommended_plans(self, value):
        self.recommended_plans_raw = json.dumps(value) if value else '[]'

    @property
    def financial_insights(self):
        try:
            return json.loads(self.financial_insights_raw) if self.financial_insights_raw else {}
        except Exception:
            return {}

    @financial_insights.setter
    def financial_insights(self, value):
        self.financial_insights_raw = json.dumps(value) if value else '{}'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'annual_income': self.annual_income,
            'dependents': self.dependents,
            'health_conditions': self.health_conditions,
            'lifestyle_habits': self.lifestyle_habits,
            'insurance_preferences': self.insurance_preferences,
            'risk_score': self.risk_score,
            'risk_factors': self.risk_factors,
            'premium_estimates': self.premium_estimates,
            'recommended_plans': self.recommended_plans,
            'financial_insights': self.financial_insights,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

class RetirementPlan(db.Model):
    __tablename__ = 'retirement_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # User Inputs
    current_age = db.Column(db.Integer, nullable=False)
    retirement_age = db.Column(db.Integer, nullable=False)
    life_expectancy = db.Column(db.Integer, default=85)
    current_savings = db.Column(db.Float, nullable=False)
    monthly_expenses = db.Column(db.Float, nullable=False)
    monthly_savings = db.Column(db.Float, nullable=False)
    expected_retirement_income = db.Column(db.Float, default=0.0)
    annual_insurance_budget = db.Column(db.Float, default=0.0)
    
    # Financial Projections
    projected_monthly_expense = db.Column(db.Float, nullable=True)
    required_corpus = db.Column(db.Float, nullable=True)
    available_corpus = db.Column(db.Float, nullable=True)
    financial_gap = db.Column(db.Float, nullable=True)
    readiness_percentage = db.Column(db.Float, nullable=True)
    additional_monthly_savings = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='pending')
    
    # Metadata and Assumptions stored as JSON
    assumptions_raw = db.Column(db.Text, nullable=True)
    recommendations_raw = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def assumptions(self):
        try:
            return json.loads(self.assumptions_raw) if self.assumptions_raw else {}
        except Exception:
            return {}

    @assumptions.setter
    def assumptions(self, value):
        self.assumptions_raw = json.dumps(value) if value else '{}'

    @property
    def recommendations(self):
        try:
            return json.loads(self.recommendations_raw) if self.recommendations_raw else []
        except Exception:
            return []

    @recommendations.setter
    def recommendations(self, value):
        self.recommendations_raw = json.dumps(value) if value else '[]'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_age': self.current_age,
            'retirement_age': self.retirement_age,
            'life_expectancy': self.life_expectancy,
            'current_savings': self.current_savings,
            'monthly_expenses': self.monthly_expenses,
            'monthly_savings': self.monthly_savings,
            'expected_retirement_income': self.expected_retirement_income,
            'annual_insurance_budget': self.annual_insurance_budget,
            'projected_monthly_expense': self.projected_monthly_expense,
            'required_corpus': self.required_corpus,
            'available_corpus': self.available_corpus,
            'financial_gap': self.financial_gap,
            'readiness_percentage': self.readiness_percentage,
            'additional_monthly_savings': self.additional_monthly_savings,
            'status': self.status,
            'assumptions': self.assumptions,
            'recommendations': self.recommendations,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


