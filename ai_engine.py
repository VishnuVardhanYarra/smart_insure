import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from carrier_api import fetch_live_carrier_quotes

# Load env files
load_dotenv()

logger = logging.getLogger(__name__)

# Configure Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully.")
else:
    logger.warning("GEMINI_API_KEY not found in environment variables. Falling back to mock recommendations.")

def format_inr(amount):
    """Format a number as Indian Rupees with Indian number system (lakhs/crores)."""
    if amount >= 10000000:
        return f"₹{amount/10000000:.1f} Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.1f} L"
    else:
        return f"₹{amount:,.0f}"

def generate_mock_recommendation(user_data):
    """
    Generates a realistic mock recommendation when the Gemini API is unavailable.
    Calculates risk scores and premium estimates in Indian Rupees (INR).
    """
    logger.info("Generating mock recommendation (INR mode)...")

    age = int(user_data.get('age', 30))
    annual_income = float(user_data.get('annual_income', 500000))  # INR
    lifestyle = (user_data.get('lifestyle_habits') or '').lower()
    health = (user_data.get('health_conditions') or '').lower()
    preferences = user_data.get('insurance_preferences') or 'Health Insurance, Term Life Insurance'

    # Base risk score
    risk_score = 25

    # Age factor
    if age > 50:
        risk_score += 25
    elif age > 35:
        risk_score += 10

    # Lifestyle factors
    risk_factors = []
    if 'smoke' in lifestyle or 'nicotine' in lifestyle or 'tobacco' in lifestyle:
        risk_score += 20
        risk_factors.append("Active smoking/nicotine usage significantly raises mortality and pulmonary disease risks.")
    if 'alcohol' in lifestyle or 'drink' in lifestyle:
        risk_score += 5
        risk_factors.append("Regular alcohol consumption increases liver disease and systemic health risks.")
    if 'sedentary' in lifestyle or 'no exercise' in lifestyle or 'inactive' in lifestyle:
        risk_score += 10
        risk_factors.append("Sedentary lifestyle significantly elevates cardiovascular and metabolic risk profile.")
    elif 'exercise' in lifestyle or 'gym' in lifestyle or 'run' in lifestyle or 'yoga' in lifestyle:
        risk_score -= 5  # Healthy habit discount

    # Health factors
    if 'diabetes' in health:
        risk_score += 15
        risk_factors.append("Pre-existing Diabetes (Type 1/2) increases circulatory and renal complication risks.")
    if 'hypertension' in health or 'blood pressure' in health or 'bp' in health:
        risk_score += 15
        risk_factors.append("Chronic hypertension raises cardiovascular event risks (stroke, heart attack).")
    if 'cancer' in health:
        risk_score += 30
        risk_factors.append("Oncological history or family predisposition requires specialized insurance riders.")
    if 'heart' in health or 'cardiac' in health:
        risk_score += 20
        risk_factors.append("Pre-existing cardiac conditions require high-coverage critical illness protection.")

    # Clamp risk score between 10 and 95
    risk_score = max(10, min(95, risk_score))

    if not risk_factors:
        risk_factors.append("Standard age-based risk profile. No high-risk lifestyle habits or pre-existing conditions reported.")

    # Premium multiplier based on risk
    premium_mult = 1.0 + (risk_score / 100.0)

    # INR-based base monthly premiums (realistic Indian market rates)
    # Term Life: ₹500-1000/month for a 30-year-old for ₹1Cr cover
    # Health: ₹800-2000/month
    # Critical Illness: ₹300-700/month
    term_life_low = int(500 * premium_mult)
    term_life_high = int(1000 * premium_mult)
    health_low = int(800 * premium_mult)
    health_high = int(2000 * premium_mult)
    ci_low = int(300 * premium_mult)
    ci_high = int(700 * premium_mult)

    premium_estimates = {
        "term_life": {
            "base_premium": f"₹{term_life_low:,} - ₹{term_life_high:,}/month",
            "factors": f"Based on age ({age} yrs) and risk profile ({risk_score}/100). Coverage up to 15-20x annual income recommended."
        },
        "health_insurance": {
            "base_premium": f"₹{health_low:,} - ₹{health_high:,}/month",
            "factors": "Includes hospitalisation, pre/post-care, and day-care procedures. Premiums reflect pre-existing condition loading."
        },
        "critical_illness": {
            "base_premium": f"₹{ci_low:,} - ₹{ci_high:,}/month",
            "factors": "Lump-sum payout on diagnosis of 36 listed critical illnesses. Premiums are directly linked to health risk factors."
        }
    }

    # Recommended plans matching preferences
    recommended_plans = []
    pref_lower = preferences.lower()

    # 1. Health Plan
    if 'health' in pref_lower or not preferences.strip():
        recommended_plans.append({
            "category": "Health Insurance",
            "plan_name": "AarogyaShield Comprehensive",
            "coverage": "₹10 Lakh",
            "estimated_premium": f"₹{int(1200 * premium_mult):,}/month",
            "why_recommended": "Covers cashless hospitalisation at 5000+ network hospitals across India. Ideal given your age and health profile to avoid catastrophic medical expenses.",
            "priority": "High" if risk_score > 40 else "Medium"
        })

    # 2. Term Life Plan
    if 'life' in pref_lower or 'term' in pref_lower or not preferences.strip():
        # Coverage = ~12x annual income, Indian norm
        coverage_amount = int(annual_income * 12)
        recommended_plans.append({
            "category": "Term Life Insurance",
            "plan_name": "SurakshaSetu Term Plan",
            "coverage": format_inr(coverage_amount),
            "estimated_premium": f"₹{int(700 * premium_mult):,}/month",
            "why_recommended": f"Provides financial security of {format_inr(coverage_amount)} to your dependents (12x annual income of {format_inr(annual_income)}). Pure term plans offer highest coverage at lowest premium.",
            "priority": "High" if int(user_data.get('dependents', 0)) > 0 else "Medium"
        })

    # 3. Critical Illness Rider
    if 'critical' in pref_lower or risk_score > 50:
        recommended_plans.append({
            "category": "Critical Illness Rider",
            "plan_name": "SankaTaaran Critical Cover",
            "coverage": "₹25 Lakh",
            "estimated_premium": f"₹{int(500 * premium_mult):,}/month",
            "why_recommended": "Provides a lump-sum of ₹25 Lakh on diagnosis of critical conditions like cancer, stroke or heart attack to cover treatment and income loss.",
            "priority": "High" if ('diabetes' in health or 'hypertension' in health or 'heart' in health) else "Medium"
        })

    # 4. Personal Accident (always recommend as a low-cost addition)
    if len(recommended_plans) < 3:
        recommended_plans.append({
            "category": "Personal Accident Cover",
            "plan_name": "RakshaCover PA Plan",
            "coverage": "₹50 Lakh",
            "estimated_premium": "₹200/month",
            "why_recommended": "Provides compensation for accidental death, permanent/partial disability. Extremely cost-effective at just ₹200/month for ₹50L coverage.",
            "priority": "Low"
        })

    # Monthly premium load as % of income
    total_monthly_premium = int((health_low + term_life_low + ci_low) * premium_mult)
    monthly_income = annual_income / 12
    premium_pct = round((total_monthly_premium / monthly_income) * 100, 1) if monthly_income > 0 else 0

    financial_insights = {
        "debt_income_ratio_analysis": (
            f"Combined estimated monthly premiums of approx {format_inr(total_monthly_premium)} represent "
            f"~{premium_pct}% of your monthly gross income of {format_inr(int(monthly_income))}. "
            f"Indian financial planning guidelines recommend keeping insurance premiums within 5-10% of monthly income."
        ),
        "emergency_fund_suggestion": (
            "Maintain a liquid emergency corpus equivalent to 6 months of expenses in a high-yield savings account or liquid mutual fund "
            "before committing to long-term insurance premiums. Consider Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY) at just ₹436/year as a starter life cover."
        ),
        "savings_opportunity": (
            "Quitting tobacco can reduce term life and health premiums by 20-40% at renewal. "
            "Opting for an annual premium payment (instead of monthly) saves 5-8% on most Indian insurance plans. "
            "Compare plans on PolicyBazaar or CoverFox for additional discounts of up to 15%."
        )
    }

    live_quotes = fetch_live_carrier_quotes(user_data, risk_score)

    return {
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "premium_estimates": premium_estimates,
        "recommended_plans": recommended_plans,
        "financial_insights": financial_insights,
        "live_carrier_quotes": live_quotes
    }


def generate_insurance_recommendation(user_data):
    """
    Calls Google Gemini AI to generate insurance recommendations in Indian Rupees.
    Falls back to mock recommendation logic if API key is invalid or query fails.
    """
    global api_key
    if not api_key:
        return generate_mock_recommendation(user_data)

    annual_income_inr = float(user_data.get('annual_income', 500000))

    prompt = f"""
    You are InsureSmart, an expert AI insurance advisor specializing in the INDIAN insurance market.
    Analyze the following user's profile and generate a comprehensive risk assessment, monthly premium estimates 
    in INDIAN RUPEES (₹), customized insurance plan recommendations, and financial planning insights.

    IMPORTANT: All currency values MUST be in Indian Rupees (INR/₹). Use Indian number format (Lakhs, Crores).
    Use Indian insurance product names and reference Indian insurers where appropriate (LIC, HDFC Life, Max Life, Star Health, ICICI Lombard, etc.)

    User Profile:
    - Name: {user_data.get('name')}
    - Age: {user_data.get('age')} years old
    - Gender: {user_data.get('gender')}
    - Annual Income: ₹{annual_income_inr:,.0f}
    - Number of Dependents: {user_data.get('dependents')}
    - Health Conditions: {user_data.get('health_conditions') if user_data.get('health_conditions') else 'None reported'}
    - Lifestyle Habits: {user_data.get('lifestyle_habits') if user_data.get('lifestyle_habits') else 'None reported'}
    - Insurance Preferences: {user_data.get('insurance_preferences') if user_data.get('insurance_preferences') else 'Health Insurance, Term Life Insurance, Critical Illness'}

    Output a JSON object with:
    1. "risk_score": integer 1-100 (lower = healthier/lower risk)
    2. "risk_factors": array of strings (key contributing factors to risk score)
    3. "premium_estimates": object with:
       - "term_life": {{"base_premium": "₹X,XXX - ₹X,XXX/month", "factors": "reason string"}}
       - "health_insurance": {{"base_premium": "₹X,XXX - ₹X,XXX/month", "factors": "reason string"}}
       - "critical_illness": {{"base_premium": "₹X,XXX - ₹X,XXX/month", "factors": "reason string"}}
    4. "recommended_plans": array of objects, each with:
       - "category": e.g. "Term Life Insurance", "Health Insurance", "Critical Illness Rider"
       - "plan_name": creative Indian-themed plan name
       - "coverage": e.g. "₹50 Lakh", "₹1 Crore"
       - "estimated_premium": e.g. "₹850/month"
       - "why_recommended": rationale targeting user profile
       - "priority": "High", "Medium", or "Low"
    5. "financial_insights": object with:
       - "debt_income_ratio_analysis": premium % vs income analysis
       - "emergency_fund_suggestion": India-specific liquidity advice
       - "savings_opportunity": India-specific premium reduction tips

    Return ONLY the valid JSON object with no extra text.
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        generation_config = {"response_mime_type": "application/json"}

        logger.info("Calling Gemini API for INR recommendations...")
        response = model.generate_content(prompt, generation_config=generation_config)

        result = json.loads(response.text.strip())

        required_keys = ["risk_score", "risk_factors", "premium_estimates", "recommended_plans", "financial_insights"]
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key '{key}' in Gemini response.")

        # Ensure recommended_plans is always a list
        if not isinstance(result.get('recommended_plans'), list):
            raise ValueError("recommended_plans must be a list.")

        # Fetch real-time live carrier quotes & attach
        result['live_carrier_quotes'] = fetch_live_carrier_quotes(user_data, result.get('risk_score', 30))
        return result

    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}. Falling back to mock generator.")
        return generate_mock_recommendation(user_data)

