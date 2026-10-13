import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import db and models
from models import db, UserRecommendation, User, RetirementPlan
from ai_engine import generate_insurance_recommendation
from retirement_engine import calculate_retirement_gap, simulate_what_if, format_inr

app = Flask(__name__)

# App Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or os.getenv('SECRET_KEY') or 'default-dev-secret-key-123'

database_url = os.getenv('DATABASE_URL')
if database_url:
    # Render and Heroku use postgres://, but SQLAlchemy requires postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Use absolute path for SQLite file to ensure it's in the correct directory
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

# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User Registration Route."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('register.html')

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "danger")
            return render_template('register.html')

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        flash("Account created successfully! Welcome to InsureSmart.", "success")
        return redirect(url_for('assess'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login Route."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == username) | (User.email == username.lower())).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('history'))

        flash("Invalid username/email or password.", "danger")
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User Logout Route."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

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
                user_id=session.get('user_id'),
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
    user_id = session.get('user_id')
    
    # Ownership check: allow access if user owns the record or if it's an unassigned guest record
    if rec.user_id and rec.user_id != user_id:
        flash("You do not have permission to view this private report.", "danger")
        return redirect(url_for('history'))
        
    return render_template('dashboard.html', rec=rec)

@app.route('/history')
def history():
    """Historical assessment listings with search capabilities (isolated per user)."""
    search_query = request.args.get('search', '').strip()
    user_id = session.get('user_id')

    # Strictly isolate history records based on logged-in user session
    if user_id:
        query = UserRecommendation.query.filter_by(user_id=user_id)
    else:
        query = UserRecommendation.query.filter_by(user_id=None)

    if search_query:
        query = query.filter(UserRecommendation.name.ilike(f"%{search_query}%"))
    
    records = query.order_by(UserRecommendation.created_at.desc()).all()
        
    return render_template('history.html', records=records, search_query=search_query)

@app.route('/api/bind_proposal', methods=['POST'])
def bind_proposal_api():
    """Real-Time Carrier Digital Proposal Binding Endpoint."""
    data = request.get_json() or {}
    quote_id = data.get('quote_id', 'QTL-DEFAULT')
    candidate_name = data.get('candidate_name', 'Client Candidate')
    
    from carrier_api import bind_policy_proposal
    res = bind_policy_proposal(quote_id, candidate_name)
    return jsonify(res)

@app.route('/api/recommendation/<int:rec_id>')
def api_recommendation(rec_id):
    """JSON API endpoint for a single record."""
    rec = UserRecommendation.query.get_or_404(rec_id)
    user_id = session.get('user_id')
    if rec.user_id and rec.user_id != user_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    return jsonify(rec.to_dict())

@app.route('/api/delete/<int:rec_id>', methods=['POST'])
def delete_recommendation(rec_id):
    """Deletes a recommendation record from history."""
    rec = UserRecommendation.query.get_or_404(rec_id)
    user_id = session.get('user_id')
    
    if rec.user_id and rec.user_id != user_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('history'))

    try:
        db.session.delete(rec)
        db.session.commit()
        flash("Record deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting record: {str(e)}")
        flash("Failed to delete record.", "danger")
    return redirect(url_for('history'))

# Retirement & What-If Scenario Simulator Routes
@app.route('/retirement')
def retirement():
    """Retirement readiness calculator and What-If scenario simulator view."""
    initial_data = {
        'current_age': request.args.get('age', 30, type=int),
        'retirement_age': request.args.get('retire_age', 60, type=int),
        'current_savings': request.args.get('savings', 500000, type=float),
        'monthly_expenses': request.args.get('expenses', 40000, type=float),
        'monthly_savings': request.args.get('monthly_savings', 15000, type=float),
        'expected_retirement_income': request.args.get('income', 0, type=float),
        'annual_insurance_budget': request.args.get('insurance', 25000, type=float)
    }
    
    saved_plans = []
    user_id = session.get('user_id')
    if user_id:
        saved_plans = RetirementPlan.query.filter_by(user_id=user_id).order_by(RetirementPlan.created_at.desc()).all()

    return render_template('retirement.html', initial_data=initial_data, saved_plans=saved_plans)

@app.route('/api/retirement/calculate', methods=['POST'])
def api_retirement_calculate():
    """Calculates retirement gap analysis for provided inputs."""
    data = request.get_json() or {}
    result = calculate_retirement_gap(data)
    
    if result.get('success') and data.get('save_to_profile') and session.get('user_id'):
        try:
            import json as json_lib
            plan = RetirementPlan(
                user_id=session.get('user_id'),
                current_age=result['current_age'],
                retirement_age=result['retirement_age'],
                life_expectancy=result['life_expectancy'],
                current_savings=result['current_savings'],
                monthly_expenses=result['monthly_expenses'],
                monthly_savings=result['monthly_savings'],
                expected_retirement_income=result['expected_retirement_income'],
                annual_insurance_budget=result['annual_insurance_budget'],
                projected_monthly_expense=result['projected_monthly_expense'],
                required_corpus=result['required_corpus'],
                available_corpus=result['total_available_corpus'],
                financial_gap=result['financial_gap'],
                readiness_percentage=result['readiness_percentage'],
                additional_monthly_savings=result['additional_monthly_savings'],
                status=result['status'],
                assumptions_raw=json_lib.dumps(result['assumptions']),
                recommendations_raw=json_lib.dumps(result['recommendations'])
            )
            db.session.add(plan)
            db.session.commit()
            result['saved_id'] = plan.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving retirement plan: {str(e)}")
            
    return jsonify(result)

@app.route('/api/retirement/simulate', methods=['POST'])
def api_retirement_simulate():
    """Simulates What-If scenario against a baseline profile."""
    data = request.get_json() or {}
    baseline = data.get('baseline', {})
    scenario = data.get('scenario', {})
    result = simulate_what_if(baseline, scenario)
    return jsonify(result)

@app.route('/api/retirement/delete/<int:plan_id>', methods=['POST'])
def delete_retirement_plan(plan_id):
    """Deletes a saved retirement plan."""
    user_id = session.get('user_id')
    plan = RetirementPlan.query.get_or_404(plan_id)
    if plan.user_id and plan.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        db.session.delete(plan)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Render and uptime monitors."""
    return jsonify({'status': 'healthy', 'service': 'insuresmart'}), 200

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content_placeholder="404 - Page Not Found"), 404

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

