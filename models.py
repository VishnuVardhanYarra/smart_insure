from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserRecommendation(db.Model):
    __tablename__ = 'user_recommendation'

    id = db.Column(db.Integer, primary_key=True)
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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
