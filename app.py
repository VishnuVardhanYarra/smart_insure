import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import db and models
from models import db, UserRecommendation
from ai_engine import generate_insurance_recommendation

app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-dev-secret-key-123')
# Use absolute path for SQLite file to ensure it's in the correct scratch directory
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'insuresmart.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# Server-side validation helper
def validate_user_input(data):
    errors = []
    
    # 1. Name validation
    name = data.get('name', '').strip()
    if not name:
        errors.append("Name is required.")
    elif len(name) < 2:
        errors.append("Name must be at least 2 characters.")
        
    # 2. Age validation
    try:
        age = int(data.get('age', 0))
        if age < 18 or age > 100:
            errors.append("Age must be between 18 and 100.")
    except ValueError:
        errors.append("Age must be a valid integer.")
        
    # 3. Gender validation
    gender = data.get('gender', '')
    if gender not in ['Male', 'Female', 'Other']:
        errors.append("Please select a valid gender option.")
        
    # 4. Income validation
    try:
        income = float(data.get('annual_income', 0))
        if income < 0:
            errors.append("Annual income cannot be negative.")
    except ValueError:
        errors.append("Annual income must be a valid number.")
        
    # 5. Dependents validation
    try:
        dependents = int(data.get('dependents', 0))
        if dependents < 0 or dependents > 20:
            errors.append("Dependents must be between 0 and 20.")
    except ValueError:
        errors.append("Number of dependents must be a valid integer.")
        
    return errors

@app.route('/')
def index():
    """Home / Landing page."""
    return render_template('index.html')

@app.route('/assess', methods=['GET', 'POST'])
def assess():
    """Multi-step assessment form collection and analysis initiation."""
    if request.method == 'POST':
        # Gather form data
        form_data = {
            'name': request.form.get('name'),
            'age': request.form.get('age'),
            'gender': request.form.get('gender'),
            'annual_income': request.form.get('annual_income'),
            'dependents': request.form.get('dependents'),
            'health_conditions': request.form.get('health_conditions'),
            'lifestyle_habits': request.form.get('lifestyle_habits'),
            'insurance_preferences': ", ".join(request.form.getlist('preferences'))
        }
        
        # Validate data
        errors = validate_user_input(form_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('assess.html', form_data=form_data)
            
        try:
            # Call AI engine to evaluate risk and recommend plans
            ai_response = generate_insurance_recommendation(form_data)
            
            # Save recommendation record in database
            rec = UserRecommendation(
                name=form_data['name'],
                age=int(form_data['age']),
                gender=form_data['gender'],
                annual_income=float(form_data['annual_income']),
                dependents=int(form_data['dependents']),
                health_conditions=form_data['health_conditions'],
                lifestyle_habits=form_data['lifestyle_habits'],
                insurance_preferences=form_data['insurance_preferences'],
                risk_score=ai_response.get('risk_score', 50),
                risk_factors=ai_response.get('risk_factors', []),
                premium_estimates=ai_response.get('premium_estimates', {}),
                recommended_plans=ai_response.get('recommended_plans', []),
                financial_insights=ai_response.get('financial_insights', {})
            )
            
            db.session.add(rec)
            db.session.commit()
            
            flash("Insurance assessment generated successfully!", "success")
            return redirect(url_for('dashboard', rec_id=rec.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing assessment: {str(e)}")
            flash(f"An unexpected error occurred during recommendation engine run: {str(e)}", "danger")
            return render_template('assess.html', form_data=form_data)
            
    return render_template('assess.html', form_data={})

@app.route('/dashboard/<int:rec_id>')
def dashboard(rec_id):
    """Detailed visual dashboard of recommendations."""
    rec = UserRecommendation.query.get_or_404(rec_id)
    return render_template('dashboard.html', rec=rec)

@app.route('/history')
def history():
    """Historical assessment listings with search capabilities."""
    search_query = request.args.get('search', '').strip()
    if search_query:
        # Search by name (case-insensitive)
        records = UserRecommendation.query.filter(
            UserRecommendation.name.ilike(f"%{search_query}%")
        ).order_by(UserRecommendation.created_at.desc()).all()
    else:
        records = UserRecommendation.query.order_by(UserRecommendation.created_at.desc()).all()
        
    return render_template('history.html', records=records, search_query=search_query)

@app.route('/api/recommendation/<int:rec_id>')
def api_recommendation(rec_id):
    """JSON API endpoint for a single record."""
    rec = UserRecommendation.query.get_or_404(rec_id)
    return jsonify(rec.to_dict())

@app.route('/api/delete/<int:rec_id>', methods=['POST'])
def delete_recommendation(rec_id):
    """Deletes a recommendation record from history."""
    rec = UserRecommendation.query.get_or_404(rec_id)
    try:
        db.session.delete(rec)
        db.session.commit()
        flash("Record deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting record: {str(e)}")
        flash("Failed to delete record.", "danger")
    return redirect(url_for('history'))

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content_placeholder="404 - Page Not Found"), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
